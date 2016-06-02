import pulsar
from pulsar import validate_list, ensure_future

from . import core
from . import commands      # noqa


exclude = set(pulsar.Config().settings)
exclude.difference_update(('config', 'log_level', 'log_handlers', 'debug'))


class Tasks(core.AgileSetting):
    name = 'tasks'
    nargs = '*'
    validator = validate_list
    default = []
    desc = "tasks to run - For the list of tasks pass -l or --list-tasks"


class ConfigFile(core.AgileSetting):
    name = "config_file"
    flags = ["--config-file"]
    default = "agile.json"
    desc = """\
        Configuration file
        """


class ListTasks(core.AgileSetting):
    name = "list_tasks"
    flags = ['-l', '--list-tasks']
    action = "store_true"
    default = False
    desc = """\
        List of available tasks
        """


class Force(core.AgileSetting):
    name = "force"
    flags = ['--force']
    action = "store_true"
    default = False
    desc = "Force execution when errors occur"


class Commit(core.AgileSetting):
    name = "commit"
    flags = ['--commit']
    action = "store_true"
    default = False
    desc = "Commit changes to git"


class Push(core.AgileSetting):
    name = "push"
    flags = ['--push']
    action = "store_true"
    default = False
    desc = "Push changes to origin"


class AgileManager(pulsar.Application, core.TaskExecutor):
    name = 'agile'
    cfg = pulsar.Config(apps=['agile'],
                        log_level=['pulsar.error', 'info'],
                        log_handlers=['console_name_level_message'],
                        description='Agile release manager',
                        exclude=exclude)
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
    def monitor_start(self, monitor, exc=None):
        self.cfg.set('workers', 0)

    async def worker_start(self, worker, exc=None):
        if not exc:
            executor = await self.executor(loop=worker._loop)
            if executor.cfg.list_tasks:
                executor.list_tasks()
            else:
                fut = ensure_future(executor(), loop=worker._loop)
                fut.add_done_callback(self._exit)

    def executor(self, **kw):
        return core.TaskExecutor.create(self.cfg, **kw)

    def _exit(self, fut):
        pulsar.arbiter().stop(exit_code=fut.result())
