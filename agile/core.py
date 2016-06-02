import os
import sys
import json
import asyncio
import logging
from collections import Mapping, OrderedDict

import pulsar

from . import utils
from .git import Git


agile_commands = {}


class AgileSetting(pulsar.Setting):
    virtual = True
    app = 'agile'
    section = "Git Agile"


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
            agile_commands[new_class.command] = new_class
        return new_class


class AgileCommand(metaclass=AgileMeta):
    """Base class for agile applications
    """
    abstract = True
    description = 'Agile command'

    def __init__(self, app):
        self.app = app

    @property
    def _loop(self):
        return self.app.http._loop

    def __call__(self, entry, cfg, options):
        """Execute a command for a given entry"""
        pass

    def __getattr__(self, name):
        return getattr(self.app, name)

    def start_server(self):
        """Start a server

        By default it does nothing
        """
        pass

    async def shell(self, command=None, **kw):
        """Execute a list of shell commands

        :param commands: list or string of shell commands
        """
        results = []
        for com in utils.as_list(command, 'shell commands should be a list'):
            com = self.render(com)
            self.logger.info('executing shell: %s', com)
            text = self.log_execute(await self.execute(com, **kw))
            if text:
                results.append(text)
        return results

    def execute(self, *args, **kwargs):
        return utils.execute(*args, **kwargs)

    def log_execute(self, text):
        if text:
            self.logger.debug(text, extra=dict(color=False))
        return text

    def context(self, *args, **kwargs):
        context = self.app.context.copy()
        context.update(*args, **kwargs)
        return context

    def as_dict(self, cfg, entry=None):
        return utils.as_dict(cfg, '%s entry not valid' % entry)

    def as_list(self, cfg, entry=None):
        return utils.as_list(cfg, '%s entry not valid' % entry)

    def with_items(self, cfg):
        with_items = cfg.get('with_items')
        if with_items:
            with_items = self.render(with_items)
            if not isinstance(with_items, list):
                raise utils.AgileError('with_items should be a list')
            return with_items

    def error(self, *args):
        return utils.AgileError(*args)


def passthrough(manager, version):
    """A simple pass through function

    :param manager: the release app
    :param version: release version
    :return: nothing
    """
    pass


def task_description(task):
    return task.get("description", "no description given")


class TaskExecutor:
    """Execute a list of tasks

    Each task is executed once the previous task is finished
    """
    @classmethod
    async def create(cls, cfg, loop=None, auth=None):
        git = await Git.create()
        gitapi = git.api(auth=auth)
        repo_path = await git.toplevel()
        return cls(cfg, git, gitapi, repo_path, loop=loop)

    def __init__(self, cfg, git, gitapi, repo_path, loop=None):
        self.cfg = cfg
        self.git = git
        self.gitapi = gitapi
        self.repo_path = repo_path
        self.logger = logging.getLogger('agile')
        self._loop = loop or asyncio.get_event_loop()
        self._running = False
        self.context = {
            'cfg': self.cfg,
            'python': sys.executable,
            'repo_path': self.repo_path
        }
        self.config = self._load_json()

    async def __call__(self):
        code = 0
        tasks = tuple(self.cfg.tasks or self.config['tasks'])
        start = False
        command = None
        try:
            assert not self._running
            self._running = True
            for task in tasks:
                try:
                    command = TaskCommand(self, task)
                    start = await command()
                except utils.AgileError as exc:
                    if self.cfg.force:
                        self.logger.error(exc)
                    else:
                        raise
                if start:
                    break
            await self.http.close()
        except utils.AgileError as exc:
            msg = '%s - %s' % (command, exc)
            self.logger.error(msg)
            code = 1
        except Exception as exc:
            self.logger.exception(str(exc))
            code = 2
        finally:
            self._running = False
        return code

    @property
    def http(self):
        return self.gitapi.http

    def render(self, text, context=None):
        """Render text if a string
        """
        if isinstance(text, list):
            return [self.render(v, context) for v in text]
        if isinstance(text, str) and '{{' in text and '}}' in text:
            return utils.render(text, context or self.context)
        else:
            return text

    def eval(self, text):
        try:
            return eval(text, {}, self.context)
        except Exception:
            raise utils.AgileError('Could not eval: "%s"' % text) from None

    def list_tasks(self):
        tasks = self.config.get('tasks')
        if not tasks:
            raise utils.AgileExit('No "tasks" entry in your %s file' %
                                  self.cfg.config_file)
        print('')
        print('==========================================')
        print('There are %d tasks available' % len(tasks))
        print('==========================================')
        print('')
        for name, task in tasks.items():
            task = utils.as_dict(
                task, 'tasks should be a dictionary of dictionaries')
            print('%s: %s' % (name, task_description(task)))
        print('')
        print('==========================================')

    def _load_json(self):
        for filename in os.listdir(self.repo_path):
            if not utils.skip_file(filename) and filename.endswith('.json'):
                entry = config_entry(filename)
                self.context[entry] = load_json(filename)
        config_file = self.cfg.config_file
        entry = config_entry(config_file)
        if entry not in self.context:
            self.context[entry] = load_json(config_file)
        return self.context.get(entry)

    async def _execute_tasks(self, tasks, start_server=False):
        start = False
        for task in tasks:
            try:
                start = start or await TaskCommand(self, task)(start_server)
            except utils.AgileError as exc:
                if self.cfg.force:
                    self.logger.error(exc)
                else:
                    raise
            if start:
                break
        return start


class TaskCommand:
    """Execute a task entry
    """
    def __init__(self, manager, task, running=None):
        self.manager = manager
        self.task = task
        self.running = set(running or ())
        if task not in self.all_tasks:
            raise utils.AgileError('No such task "%s"' % task)
        self.info = utils.as_dict(self.all_tasks[task],
                                  'Task should be a dictionary')
        self.commands = utils.as_list(self.info.get('command'),
                                      'No command entry for "%s" task' % task)
        self.running.add(task)

    def __repr__(self):
        return self.task
    __str__ = __repr__

    @property
    def all_tasks(self):
        return self.manager.config['tasks']

    async def __call__(self, start_server=False):
        self.manager.logger.info('Executing "%s" task - %s' %
                                 (self.task, task_description(self.info)))
        started = False
        for command in self.commands:
            extra = None

            if isinstance(command, Mapping):
                extra = command
                command = extra.pop('command', None)

            if not command:
                raise utils.AgileError('command not defined')

            if command in self.running:
                raise utils.AgileError('command already running')

            try:
                self.check_conditions(extra)

                if command in self.all_tasks:
                    # the command is another task
                    command = TaskCommand(self.manager, command, self.running)
                    st = await command(start_server)
                else:
                    st = await self._execute(command, start_server)
                started = started or st
            except utils.AgileSkip:
                self.manager.logger.info('Skip command %s', command)
        return started

    def check_conditions(self, extra):
        if not extra:
            return

        if 'when' in extra and not self.manager.eval(extra['when']):
            raise utils.AgileSkip

    async def _execute(self, command, start=False):
        bits = command.split(':')
        key = bits[0]
        entry = None
        if len(bits) == 2:
            entry = bits[1]
        elif len(bits) > 2:
            raise utils.AgileError('bad command %s' % command)

        manager = self.manager
        Command = agile_commands.get(key)
        if not Command:
            raise utils.AgileError('No such command "%s"' % key)

        config = manager.config.get(key)
        if not config:
            raise utils.AgileError('No entry "%s" in %s' %
                                   (key, manager.cfg.config_file))

        config = config.copy()
        options = config.pop('options', {})
        app = Command(manager)

        if entry is not None:
            cfg = config.get(entry)
            if not cfg:
                raise utils.AgileError('No entry "%s" in %s' %
                                       (command, manager.cfg.config_file))
            start = await app(entry, app.as_dict(cfg, entry), options)
        else:
            for entry, cfg in config.items():
                start = await app(entry, app.as_dict(cfg, entry), options)

        if start:
            return app.start_server()


def load_json(filename):
    with open(filename, 'r') as file:
        text = file.read()
    decoder = json.JSONDecoder(object_pairs_hook=OrderedDict)
    return decoder.decode(text)


def config_entry(filename):
    entry = filename.split('.')[0]
    return entry.replace('/', '.')
