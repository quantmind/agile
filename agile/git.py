from urllib.parse import urlsplit

from pulsar import ImproperlyConfigured

from .github import GithubApi
from . import utils


class Git:

    @classmethod
    async def create(cls):
        remote = await utils.execute('git config --get remote.origin.url')
        raw = remote.split('@')
        if len(raw) == 2:
            raw = raw[1]
            domain, path = raw.split(':')
        else:
            p = urlsplit(remote)
            domain = p.netloc
            path = p.path

        if not path.endswith('.git'):
            raise ImproperlyConfigured('Remote origin "%s" not supprted' %
                                       remote)
        path = path[:-4]

        if domain == 'github.com':
            return Github(domain, path)
        else:
            return Gitlab(domain, path)

    def __init__(self, domain, path):
        self.domain = domain
        self.repo_path = path

    def __repr__(self):
        return self.domain
    __str__ = __repr__

    def api(self):
        raise NotImplementedError

    async def toplevel(self):
        """Top level directory for the repository
        """
        level = await utils.execute('git rev-parse --show-toplevel')
        return level

    async def branch(self):
        name = await utils.execute('git rev-parse --abbrev-ref HEAD')
        return name

    async def add(self, *files):
        if files:
            result = await utils.execute('git add %s' % ' '.join(files))
            return result

    async def commit(self, *files, msg=None):
        if not files:
            files = ('-a',)
        files = list(files)
        files.append('-m')
        files.append(msg or 'commit from pulsar.release manager')
        result = await utils.execute('git commit %s' % ' '.join(files))
        return result

    async def push(self):
        name = await self.branch()
        result = await utils.execute('git push origin %s' % name)
        if '[rejected]' in result:
            raise RuntimeError(result)
        return result


class Github(Git):

    def api(self, **kw):
        return GithubApi(**kw)


def Gitlab(Git):
    pass
