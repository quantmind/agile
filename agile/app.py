import os
import sys
import json
import logging
from string import Template
from collections import OrderedDict

import pulsar
from pulsar import ensure_future, ImproperlyConfigured, validate_list

from .git import Git
from .utils import (TaskCommand, AgileSetting, AgileError, AgileExit,
                    task_description)


exclude = set(pulsar.Config().settings)
exclude.difference_update(('config', 'loglevel', 'loghandlers', 'debug'))


class Tasks(AgileSetting):
    name = 'tasks'
    nargs = '*'
    validator = validate_list
    default = []
    desc = "tasks to run - For the list of tasks pass -l or --list-tasks"


class ConfigFile(AgileSetting):
    name = "config_file"
    flags = ["--config-file"]
    default = "agile.json"
    desc = """\
        Configuration file
        """


class ListTasks(AgileSetting):
    name = "list_tasks"
    flags = ['-l', '--list-tasks']
    action = "store_true"
    default = False
    desc = "List of available tasks"


class Force(AgileSetting):
    name = "force"
    flags = ['--force']
    action = "store_true"
    default = False
    desc = "Force execution when errors occur"


class Commit(AgileSetting):
    name = "commit"
    flags = ['--commit']
    action = "store_true"
    default = False
    desc = "Commit changes to git"


class AgileManager(pulsar.Application):
    name = 'agile'
    cfg = pulsar.Config(apps=['agile'],
                        loglevel=['pulsar.error', 'info'],
                        loghandlers=['console_name_level_message'],
                        description='Agile release manager',
                        exclude=exclude)
    git = None
    gitapi = None
    config = None
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
            ensure_future(self._start_agile(worker))

    def render(self, text):
        context = self.context
        return Template(text).safe_substitute(context) if context else text

    def agile(self):
        """ Execute a set of tasks agains a configuration file

        :return: status code (0 - no errors, 1 - errors, 2 - critical errors)
        """
        self.context = {'python': sys.executable}
        self.logger = logging.getLogger('agile')
        exit_code = 1
        try:
            self.git = yield from Git.create()
            self.gitapi = self.git.api()
            self.repo_path = yield from self.git.toplevel()
            self.context['repo_path'] = self.repo_path
            self.logger.debug('Repository directory %s', self.repo_path)
            self.config = self._load_agile_config()
            if self.cfg.list_tasks:
                self._list_tasks()
            else:
                yield from self._execute()
        except AgileExit as exc:
            self.logger.error(str(exc))
        except (ImproperlyConfigured, AgileError) as exc:
            self.logger.error(str(exc))
            self.logger.info('Execution stopped. '
                             'Pass --force to force executions on errors')
        except Exception as exc:
            self.logger.exception(str(exc))
            exit_code = 2
        else:
            exit_code = 0

        return exit_code

    def _start_agile(self, worker):
        exit_code = yield from self.agile()
        if self.gitapi:
            self.gitapi.http.close()
        worker._loop.call_soon(self._exit, exit_code)

    def _execute(self):
        tasks = tuple(self.cfg.tasks or self.config['tasks'])
        for task in tasks:
            try:
                yield from TaskCommand(self, task)()
            except (ImproperlyConfigured, AgileError) as exc:
                if self.cfg.force:
                    self.logger.error(exc)
                else:
                    raise

    def _list_tasks(self):
        tasks = self.config.get('tasks')
        if not tasks:
            raise AgileExit('No "tasks" entry in your %s file' %
                            self.cfg.config_file)
        print('')
        print('==========================================')
        print('There are %d tasks available' % len(tasks))
        print('==========================================')
        print('')
        for name, task in tasks.items():
            print('%s: %s' % (name, task_description(task)))
        print('')
        print('==========================================')

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
