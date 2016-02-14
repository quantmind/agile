import os
import json
import logging
from string import Template
from collections import OrderedDict

import pulsar
from pulsar import ensure_future, ImproperlyConfigured, as_coroutine

from .git import Git
from .utils import agile_apps, AgileSetting


exclude = set(pulsar.Config().settings)
exclude.difference_update(('config', 'loglevel', 'debug'))


class Command(AgileSetting):
    name  = 'commands'
    nargs = '*'
    desc = "command to run - For a list of command --list-commands"


class ConfigFile(AgileSetting):
    name = "config_file"
    flags = ["--config-file"]
    default = "agile.json"
    desc = """\
        Configuration file
        """


class Commit(AgileSetting):
    name = "list_commands"
    flags = ['-l', '--list-commands']
    action = "store_true"
    default = False
    desc = "List available commands"


class AgileManager(pulsar.Application):
    name = 'agile'
    cfg = pulsar.Config(apps=['agile'],
                        loglevel=['pulsar.error', 'info'],
                        description='Agile release manager',
                        exclude=exclude)
    git = None
    gitapi = None
    note_file = None
    context = None
    repo_path = None
    """Path of repository
    """
    releases_path = None
    """Path to the location of release configuration files
    """
    @property
    def http(self):
        return self.gitapi.http if self.gitapi else None

    def monitor_start(self, monitor, exc=None):
        cfg = self.cfg
        cfg.set('workers', 0)

    def worker_start(self, worker, exc=None):
        if not exc:
            worker._loop.call_soon(ensure_future, self._start_agile(worker))

    def render(self, text):
        context = self.context
        return Template(text).safe_substitute(context) if context else text

    def _start_agile(self, worker):
        self.context = {}
        self.logger = logging.getLogger('agile')
        exit_code = 1
        later = 1
        try:
            if self.cfg.list_commands:
                self._list_commands()
                later = 0
            else:
                yield from self._execute(worker)
        except ImproperlyConfigured as exc:
            self.logger.error(str(exc))
        except Exception as exc:
            self.logger.exception(str(exc))
        else:
            exit_code = None

        if self.gitapi:
            self.gitapi.http.close()
        self.logger.info("Exiting")
        worker._loop.call_later(later, self._exit, exit_code)

    def _execute(self, worker):
        self.git = yield from Git.create()
        self.gitapi = self.git.api()
        self.repo_path = yield from self.git.toplevel()
        self.context['repo_path'] = self.repo_path
        self.logger.info('Repository directory %s', self.repo_path)
        self.config = self._load_agile_config()
        yield from agile_apps(self)

    def _list_commands(self):
        print('')
        for App in agile_apps:
            print('%s: %s' % (App.command, App.description))
        print('')

    def _exit(self, exit_code):
        pulsar.arbiter().stop(exit_code=exit_code)

    def _load_agile_config(self):
        config_file = os.path.join(self.repo_path, self.cfg.config_file)
        if not os.path.isfile(config_file):
            raise ImproperlyConfigured('No %s file' % config_file)
        # Load release config and notes
        with open(config_file, 'r') as file:
            config = file.read()
        decoder = json.JSONDecoder(object_pairs_hook=OrderedDict)
        return decoder.decode(config)
