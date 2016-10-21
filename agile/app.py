import pulsar
from pulsar import validate_list, ensure_future, HaltServer

from . import core
from . import actions      # noqa
from . import plugins      # noqa


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
    name = "list_commands"
    flags = ['-l', '--list-commands']
    action = "store_true"
    default = False
    desc = """\
        List of available commands
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


class Environ(core.AgileSetting):
    name = "environ"
    flags = ['--environ']
    action = "store_true"
    default = False
    desc = "Show the environment and exit"


class AgileManager(pulsar.Application):
    name = 'agile'
    cfg = pulsar.Config(apps=['agile'],
                        log_level=['pulsar.error', 'info'],
                        log_handlers=['console_name_level_message'],
                        description='Agile release manager',
                        exclude=exclude)

    def monitor_start(self, monitor, exc=None):
        self.cfg.set('workers', 0)

    async def worker_start(self, worker, exc=None):
        if not exc:
            try:
                print(self.script)
                executor = await self.executor(loop=worker._loop)
            except Exception:
                self.logger.exception('Could not initialise')
                worker._loop.call_soon(self.done, 2)
            else:
                if executor.cfg.list_commands:
                    executed = executor.list_commands()
                elif executor.cfg.environ:
                    executed = executor.show_environ()
                else:
                    executed = executor.run()
                fut = ensure_future(executed, loop=worker._loop)
                fut.add_done_callback(self._exit)

    def executor(self, **kw):
        return core.CommandExecutor.create(self.cfg, **kw)

    def done(self, exit_code=None):
        exit_code = exit_code or 0
        if exit_code < 3:
            raise HaltServer(exit_code=exit_code)

    def _exit(self, fut):
        self.done(exit_code=fut.result())
