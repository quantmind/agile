import os
import sys
import glob
from asyncio import ensure_future

from .. import utils


_win = (sys.platform == "win32")


class Watch(utils.AgileApp, utils.TaskExecutor):
    """Run shell commands
    """
    description = ('Watch for changes on file system and execute commands '
                   'on the shell')
    watching = None

    async def __call__(self, name, config, options):
        files = utils.as_list(config.get('files'), 'files entry not valid')
        tasks = utils.as_list(config.get('command'), 'command entry not valid')
        if self.watching is None:
            self.all_files = {}
            self.watching = []
        self.watching.append((files, tasks))

    def start_server(self):
        self._loop.call_later(1, ensure_future, self.watch())
        self.logger.info('Started watching server')
        return True

    async def watch(self):
        for files, tasks in self.watching:
            try:
                await self.check(files, tasks)
            except Exception:
                self.logger.exception('Exception while watching %s',
                                      str(files))
        self._loop.call_later(1, ensure_future, self.watch())

    async def check(self, files, tasks):
        filename = self.changed(files)
        if filename:
            self.logger.info('Changes in "%s"', filename)
            await self.execute_tasks(tasks)
            self.logger.info('Finished with "%s" changes', filename)

    def changed(self, files):
        for src in files:
            for filename in glob.glob(src):
                stat = os.stat(filename)
                mtime = stat.st_mtime
                if _win:
                    mtime -= stat.st_ctime
                current = self.all_files.get(filename)
                if current is None:
                    self.all_files[filename] = mtime
                    continue
                elif mtime != current:
                    self.all_files[filename] = mtime
                    return filename
