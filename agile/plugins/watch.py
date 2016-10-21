import os
import sys
from asyncio import ensure_future

import glob2 as glob

from .. import core


_win = (sys.platform == "win32")


class Watch(core.AgileCommand):
    description = 'Watch for changes on file system and execute commands'
    watching = None
    _waiter = None

    async def run(self, name, config, options):
        files = self.as_list(config.get('files'), 'files entry not valid')
        tasks = self.as_list(config.get('command'), 'command entry not valid')
        if self.watching is None:
            self.all_files = {}
            self.watching = []
        self.watching.append((files, tasks))

    def start_server(self):
        self._loop.call_later(1, self._watch)
        self.logger.info('Started watch server')
        return True

    async def watch(self):
        for files, tasks in self.watching:
            try:
                await self.check(files, tasks)
            except Exception:
                self.logger.exception('Exception while watching %s',
                                      str(files))
        self._loop.call_later(1, self._watch)

    async def check(self, files, tasks):
        filename = self.changed(files)
        if filename:
            self.logger.warning('CHANGES in "%s"', filename)
            await self.executor.run(tasks)
            self.logger.info('FINISHED with "%s" changes', filename)

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

    def _watch(self):
        self._waiter = ensure_future(self.watch())
