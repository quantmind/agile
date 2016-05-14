import os
import json
import asyncio
import logging
import configparser
from collections import Mapping, OrderedDict

import pulsar
from pulsar import ImproperlyConfigured

from jinja2 import Template


class AgileError(Exception):
    pass


class AgileExit(AgileError):
    pass


class ShellError(AgileError):

    def __init__(self, msg, code):
        super().__init__(msg)
        self.code = code


class AgileApps(dict):

    async def __call__(self, manager, command, start=False):
        bits = command.split(':')
        key = bits[0]
        entry = None
        if len(bits) == 2:
            entry = bits[1]
        elif len(bits) > 2:
            raise ImproperlyConfigured('bad command %s' % command)

        App = self.get(key)
        if not App:
            raise ImproperlyConfigured('No such command "%s"' % key)

        config = manager.config.get(key)
        if not config:
            raise ImproperlyConfigured('No entry "%s" in %s' %
                                       (key, manager.cfg.config_file))

        config = config.copy()
        options = config.pop('options', {})
        app = App(manager)

        if entry is not None:
            cfg = config.get(entry)
            if not cfg:
                raise ImproperlyConfigured('No entry "%s" in %s' %
                                           (command, manager.cfg.config_file))
            cfg = app.as_dict(cfg, entry)
            await app(entry, cfg, options)
        else:
            for entry, cfg in config.items():
                cfg = app.as_dict(cfg, entry)
                await app(entry, cfg, options)
            if start:
                return app.start_server()


agile_apps = AgileApps()


class AgileMeta(type):
    """A metaclass which collects all setting classes and put them
    in the global ``KNOWN_SETTINGS`` list.
    """
    def __new__(cls, name, bases, attrs):
        abstract = attrs.pop('abstract', False)
        attrs['command'] = attrs.pop('command', name.lower())
        new_class = super().__new__(cls, name, bases, attrs)
        new_class.logger = logging.getLogger('agile.%s' % new_class.command)
        if not abstract:
            agile_apps[new_class.command] = new_class
        return new_class


class AgileApp(metaclass=AgileMeta):
    """Base class for agile applications
    """
    abstract = True
    description = 'Agile application'

    def __init__(self, app):
        self.app = app

    @property
    def _loop(self):
        return self.app.http._loop

    def __call__(self, entry, cfg, options):
        pass

    def __getattr__(self, name):
        return getattr(self.app, name)

    def start_server(self):
        """Start a server

        By default it does nothing
        """
        pass

    async def shell(self, name, coms, **kw):
        """Execute a list of shell commands
        """
        results = []
        for com in as_list(coms, 'shell commands should be a list'):
            com = self.render(com)
            self.logger.info('executing shell:%s - %s', name, com)
            text = self.log_execute(await execute(com))
            if text:
                results.append(text)
        return results

    def log_execute(self, text):
        if text:
            self.logger.debug(text, extra=dict(color=False))
        return text

    def as_dict(self, cfg, entry):
        return as_dict(cfg, '%s entry not valid' % entry)


class AgileSetting(pulsar.Setting):
    virtual = True
    app = 'agile'
    section = "Git Agile"


async def execute(command):
    """Execute a shell command
    :param args: a given number of command parameters
    :return: the output text
    """
    proc = await asyncio.create_subprocess_shell(
        command, stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT)
    await proc.wait()
    msg = await proc.stdout.read()
    msg = msg.decode('utf-8').strip()
    if proc.returncode:
        raise ShellError(msg, proc.returncode)
    return msg


def passthrough(manager, version):
    """A simple pass through function

    :param manager: the release app
    :param version: release version
    :return: nothing
    """
    pass


def skipfile(name):
    return name.startswith('.') or name.startswith('__')


def render(text, context):
    template = Template(text)
    return template.render(**context)


def semantic_version(tag):
    """Get a valid semantic version for tag
    """
    try:
        version = list(map(int, tag.split('.')))
        assert len(version) == 3
        return tuple(version)
    except Exception as exc:
        raise ImproperlyConfigured('Could not parse "%s", please use '
                                   'MAJOR.MINOR.PATCH' % tag) from exc


def get_auth():
    """Return a tuple for authenticating a user

    If not successful raise ``ImproperlyConfigured``.
    """
    home = os.path.expanduser("~")
    config = os.path.join(home, '.gitconfig')
    if not os.path.isfile(config):
        raise ImproperlyConfigured('.gitconfig file not available in %s'
                                   % home)

    parser = configparser.ConfigParser()
    parser.read(config)
    if 'user' in parser:
        user = parser['user']
        if 'username' not in user:
            raise ImproperlyConfigured('Specify username in %s user '
                                       'section' % config)
        if 'token' not in user:
            raise ImproperlyConfigured('Specify token in %s user section'
                                       % config)
        return user['username'], user['token']
    else:
        raise ImproperlyConfigured('No user section in %s' % config)


def as_list(entry, msg=None):
    if entry and not isinstance(entry, list):
        entry = [entry]
    if not entry:
        raise ImproperlyConfigured(msg or 'Not a valid entry')
    return entry


def as_dict(entry, msg=None):
    if not isinstance(entry, Mapping):
        raise ImproperlyConfigured(msg or 'Not a valid entry')
    return entry


def task_description(task):
    return task.get("description", "no description given")


class TaskExecutor:

    async def execute_tasks(self, tasks, start_server=False):
        start = False
        for task in tasks:
            try:
                start = start or await TaskCommand(self, task)(start_server)
            except (ImproperlyConfigured, AgileError) as exc:
                if self.cfg.force:
                    self.logger.error(exc)
                else:
                    raise
        return start


class TaskCommand:

    def __init__(self, manager, task, running=None):
        self.manager = manager
        self.task = task
        self.running = set(running or ())
        if task not in self.all_tasks:
            raise ImproperlyConfigured('No such task "%s"' % task)
        self.info = as_dict(self.all_tasks[task],
                            'Task should be a dictionary')
        self.commands = as_list(self.info.get('command'),
                                'No command entry for "%s" task' % task)
        self.running.add(task)

    @property
    def all_tasks(self):
        return self.manager.config['tasks']

    async def __call__(self, start_server=False):
        self.manager.logger.info('Executing "%s" task - %s' %
                                 (self.task, task_description(self.info)))
        started = False
        for command in self.commands:
            if command in self.running:
                raise ImproperlyConfigured('command already running')

            if command in self.all_tasks:
                # the command is another task
                command = TaskCommand(self.manager, command, self.running)
                st = await command(start_server)
            else:
                st = await agile_apps(self.manager, command, start_server)
            started = started or st
        return started


def load_json(filename):
    with open(filename, 'r') as file:
        text = file.read()
    decoder = json.JSONDecoder(object_pairs_hook=OrderedDict)
    return decoder.decode(text)


def config_entry(filename):
    entry = filename.split('.')[0]
    return entry.replace('/', '.')
