import os
import sys
import logging

import pulsar
from pulsar import ensure_future, ImproperlyConfigured, validate_list

from .git import Git
from . import utils
from . import commands      # noqa


exclude = set(pulsar.Config().settings)
exclude.difference_update(('config', 'loglevel', 'loghandlers', 'debug'))


class Tasks(utils.AgileSetting):
    name = 'tasks'
    nargs = '*'
    validator = validate_list
    default = []
    desc = "tasks to run - For the list of tasks pass -l or --list-tasks"


class ConfigFile(utils.AgileSetting):
    name = "config_file"
    flags = ["--config-file"]
    default = "agile.json"
    desc = """\
        Configuration file
        """


class ListTasks(utils.AgileSetting):
    name = "list_tasks"
    flags = ['-l', '--list-tasks']
    action = "store_true"
    default = False
    desc = """\
        List of available tasks
        """


class Force(utils.AgileSetting):
    name = "force"
    flags = ['--force']
    action = "store_true"
    default = False
    desc = "Force execution when errors occur"


class Commit(utils.AgileSetting):
    name = "commit"
    flags = ['--commit']
    action = "store_true"
    default = False
    desc = "Commit changes to git"


class Push(utils.AgileSetting):
    name = "push"
    flags = ['--push']
    action = "store_true"
    default = False
    desc = "Push changes to origin"


class AgileManager(pulsar.Application, utils.TaskExecutor):
    name = 'agile'
    cfg = pulsar.Config(apps=['agile'],
                        log_level=['pulsar.error', 'info'],
                        log_handlers=['console_name_level_message'],
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
            ensure_future(self._agile(worker))

    def render(self, text):
        context = self.context
        return utils.render(text, context) if context else text

    async def agile(self):
        """ Execute a set of tasks against a configuration file
        """
        self.logger = logging.getLogger('agile')
        self.context = {'python': sys.executable}
        self.git = await Git.create()
        self.gitapi = self.cfg.get('gitapi', self.git.api())
        self.repo_path = await self.git.toplevel()
        self.context['repo_path'] = self.repo_path
        self.logger.debug('Repository directory %s', self.repo_path)
        self.config = self._load_json()
        if self.cfg.list_tasks:
            self._list_tasks()
        else:
            tasks = tuple(self.cfg.tasks or self.config['tasks'])
            return await self.execute_tasks(tasks, True)

    async def _agile(self, worker):   # pragma    nocover
        exit_code = 1
        started = False
        try:
            started = await self.agile()
        except utils.AgileExit as exc:
            self.logger.error(str(exc))
        except (ImproperlyConfigured, utils.AgileError) as exc:
            self.logger.error(str(exc))
            self.logger.info('Execution stopped. '
                             'Pass --force to force executions on errors')
        except Exception as exc:
            self.logger.exception(str(exc))
            exit_code = 2
        else:
            exit_code = 0
        if not started:
            if self.gitapi:
                await self.gitapi.http.close()
            worker._loop.call_soon(self._exit, exit_code)

    def _list_tasks(self):
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
            print('%s: %s' % (name, utils.task_description(task)))
        print('')
        print('==========================================')

    def _exit(self, exit_code):
        pulsar.arbiter().stop(exit_code=exit_code)

    def _load_json(self):
        for filename in os.listdir(self.repo_path):
            if not utils.skipfile(filename) and filename.endswith('.json'):
                entry = utils.config_entry(filename)
                self.context[entry] = utils.load_json(filename)
        config_file = self.cfg.config_file
        entry = utils.config_entry(config_file)
        if entry not in self.context:
            self.context[entry] = utils.load_json(config_file)
        return self.context.get(entry)
