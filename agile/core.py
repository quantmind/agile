import os
import sys
import json
import logging
from collections import Mapping, OrderedDict

import pulsar
from pulsar.apps.http import HttpClient

from . import utils
from .git import Git


agile_always = OrderedDict()
agile_commands = OrderedDict()
agile_actions = OrderedDict()


class AgileSetting(pulsar.Setting):
    virtual = True
    app = 'agile'
    section = "Git Agile"


class Agile:

    @property
    def _loop(self):
        return self.http._loop

    def as_dict(self, cfg, entry=None):
        return utils.as_dict(cfg, '%s entry not valid' % entry)

    def as_list(self, cfg, entry=None):
        return utils.as_list(cfg, '%s entry not valid' % entry)

    def new_context(self, *args, **kwargs):
        context = self.executor.context.copy()
        context.update(*args, **kwargs)
        return context

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


class AgileMeta(type):
    """A metaclass which collects all setting classes and put them
    in the global ``KNOWN_SETTINGS`` list.
    """
    def __new__(cls, name, bases, attrs):
        abstract = attrs.pop('abstract', False)
        attrs['key'] = attrs.pop('key', name.lower())
        new_class = super().__new__(cls, name, bases, attrs)
        new_class.logger = logging.getLogger('agile.%s' % new_class.key)
        if not abstract:
            if issubclass(new_class, AgileAction):
                agile_actions[new_class.key] = new_class
            else:
                agile_commands[new_class.key] = new_class
                if new_class.always:
                    agile_always[new_class.key] = new_class
        return new_class


class AgileBase(Agile, metaclass=AgileMeta):
    abstract = True

    def __init__(self, executor):
        self.executor = executor

    @property
    def http(self):
        return self.executor.http


class AgileAction(AgileBase):
    abstract = True

    def run(self, options):
        pass


class AgileCommand(AgileBase):
    """Base class for agile applications
    """
    abstract = True
    always = False
    description = 'Agile command'

    def run(self, entry, cfg, options):
        """Execute a command for a given entry"""
        pass

    def __getattr__(self, name):
        return getattr(self.executor, name)

    def start_server(self):
        """Start a server

        By default it does nothing
        """
        pass

    async def shell(self, command=None, context=None, **kw):
        """Execute a list of shell commands

        :param commands: list or string of shell commands
        """
        results = []
        for com in utils.as_list(command, 'shell commands should be a list'):
            com = self.render(com, context=context)
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

    def with_items(self, cfg):
        with_items = cfg.get('with_items')
        if with_items:
            if isinstance(with_items, str):
                with_items = self.eval(with_items)
            if not isinstance(with_items, list):
                raise utils.AgileError('with_items should be a list')
            return with_items

    def error(self, *args):
        return utils.AgileError(*args)


def passthrough(executor, version):
    """A simple pass through function

    :param executor: the executor
    :param version: release version
    :return: nothing
    """
    pass


def task_description(task):
    if isinstance(task, Mapping):
        return task.get("description", "no description given")
    return task.description


async def execute_commands(agile, commands, options):
    started = None
    for command in commands:
        extra = None

        if isinstance(command, Mapping):
            extra = command
            command = extra.pop('command', None)

        if not command:
            raise utils.AgileError('command not defined')

        try:

            agile.executor.apply_actions(extra)
            started = await execute_command(agile, command, options)
            if started:
                break
        except utils.AgileSkip:
            agile.logger.info('Skip command %s', command)
    return started


async def execute_command(agile, command, options):
    bits = command.split(':')
    key = bits[0]
    entry = None
    if len(bits) == 2:
        entry = bits[1]
    elif len(bits) > 2:
        raise utils.AgileError('bad command %s' % command)

    Command = agile_commands.get(key)
    if not Command:
        raise utils.AgileError('No such command "%s"' % key)

    config = agile.config.get(key)
    if not config:
        if Command.always:
            return
        raise utils.AgileError('No entry "%s" in %s' %
                               (key, agile.cfg.config_file))

    config = config.copy()
    opts = options.copy()
    opts.update(config.pop('options', {}))
    agile = Command(agile.executor)

    if entry is not None:
        cfg = config.get(entry)
        if not cfg:
            raise utils.AgileError('No entry "%s" in %s' %
                                   (command, agile.cfg.config_file))
        await agile.run(entry, agile.as_dict(cfg, entry), opts)
    else:
        for entry, cfg in config.items():
            await agile.run(entry, agile.as_dict(cfg, entry), opts)

    return agile.start_server()


class CommandExecutor(Agile):
    """Execute commands

    Each command is executed once the previous command has finished
    """
    @classmethod
    async def create(cls, cfg, loop=None, auth=None):
        http = HttpClient(loop=loop)
        try:
            git = await Git.create()
            gitapi = git.api(auth=auth, http=http)
            repo_path = await git.toplevel()
        except Exception:
            git = gitapi = repo_path = None
        return cls(cfg, http, git, gitapi, repo_path)

    def __init__(self, cfg, http, git, gitapi, repo_path):
        self.cfg = cfg
        self.git = git
        self.gitapi = gitapi
        self.repo_path = repo_path
        self.logger = logging.getLogger('agile')
        self.http = http
        self._running = False
        self.context = {
            'cfg': self.cfg,
            'python': sys.executable,
            'repo_path': self.repo_path
        }
        self.config = self._load_json()
        self.actions = (((key, Action(self)) for key, Action
                         in agile_actions.items()))

    @property
    def executor(self):
        return self

    def apply_actions(self, options):
        if not options:
            return
        for action in self.actions.values():
            action(options)

    @utils.safe
    async def run(self, commands=None):
        names = list(agile_always)
        if commands is None:
            commands = self.cfg.tasks
        names.extend(commands)
        if await execute_commands(self, names, {}):
            return 3
        else:
            await self.http.close()

    @utils.safe
    async def list_commands(self):
        count = 0
        for key in sorted(self.config):
            Command = agile_commands.get(key)
            if Command and not Command.always:
                commands = utils.as_dict(
                    self.config.get(key),
                    'Plugin %s should be a dictionary of commands' % key
                )
                print('')
                print('%s: %s' % (key, task_description(Command)))
                print('==========================================')
                for name in sorted(commands):
                    count += 1
                    full_name = '%s:%s' % (key, name)
                    cfg = utils.as_dict(
                        commands.get(name),
                        'Command %s should be a dictionary of commands' %
                        full_name
                    )
                    print('%s: %s' % (full_name, task_description(cfg)))
                print('==========================================')

        print('')
        print('There are %d commands available' % count)
        print('')

    @utils.safe
    async def show_environ(self):
        ctx = self.context.copy()
        name = self.cfg.config_file.split('.')[0]
        ctx.pop(name, None)
        ctx['cfg'] = dict(((name, s.value) for name, s in
                           self.cfg.settings.items()))
        print(json.dumps(ctx, indent=4))

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


def load_json(filename):
    with open(filename, 'r') as file:
        text = file.read()
    decoder = json.JSONDecoder(object_pairs_hook=OrderedDict)
    return decoder.decode(text)


def config_entry(filename):
    entry = filename.split('.')[0]
    return entry.replace('/', '.')
