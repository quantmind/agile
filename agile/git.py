import asyncio
import logging

from .github import GithubApi


class Git:

    @classmethod
    def create(cls):
        remote = yield from cls.execute('git', 'config', '--get',
                                        'remote.origin.url')
        raw = remote.split('@')
        assert len(raw), 2
        raw = raw[1]
        domain, path = raw.split(':')
        assert path.endswith('.git')
        path = path[:-4]
        if domain == 'github.com':
            return Github(domain, path)
        else:
            return Gitlab(domain, path)

    @classmethod
    def execute(cls, *args):
        proc = yield from asyncio.create_subprocess_exec(
            *args, stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT)
        yield from proc.wait()
        data = yield from proc.stdout.read()
        return data.decode('utf-8').strip()

    def __init__(self, domain, path):
        self.domain = domain
        self.repo_path = path
        self.logger = logging.getLogger('pulsar.release')

    def __repr__(self):
        return self.domain
    __str__ = __repr__

    def api(self):
        raise NotImplementedError

    def toplevel(self):
        level = yield from self.execute('git', 'rev-parse', '--show-toplevel')
        return level

    def branch(self):
        name = yield from self.execute('git', 'rev-parse',
                                       '--abbrev-ref', 'HEAD')
        return name

    def add(self, *files):
        if files:
            result = yield from self.execute('git', 'add', *files)
            return result

    def commit(self, *files, msg=None):
        if not files:
            files = ('-a',)
        files = list(files)
        files.append('-m')
        files.append(msg or 'commit from pulsar.release manager')
        result = yield from self.execute('git', 'commit', *files)
        return result

    def push(self):
        name = yield from self.branch()
        result = yield from self.execute('git', 'push', 'origin', name)
        if '[rejected]' in result:
            raise RuntimeError(result)
        return result


class Github(Git):

    def api(self):
        return GithubApi()


def Gitlab(Git):
    pass
