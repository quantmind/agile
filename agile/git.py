from urllib.parse import urlsplit

from pulsar import ImproperlyConfigured

from .github import GithubApi
from . import utils


class Git:
    """Asynchronous git commands.

    Usage:

        git = await Git.create()

    This will return a git object configured against the local repository
    """
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
        return await utils.execute('git rev-parse --show-toplevel')

    async def branch(self):
        """Return the current branch name
        """
        return await utils.execute('git rev-parse --abbrev-ref HEAD')

    async def add(self, *files):
        """Add files to the repo"""
        if files:
            return await utils.execute('git add %s' % ' '.join(files))

    async def rm(self, *files, flags=None):
        """Remove files to the repo

        :param flags: additional string of flags such as --cached -r, ...
        """
        if files:
            flags = flags or ''
            return await utils.execute('git rm %s %s' %
                                       (flags, ' '.join(files)))

    async def commit(self, *files, msg=None):
        """Commit ``fiels`` into the repo
        :param files: optional fiels, otherwise all are assumed
        :param msg: optional message
        :return: message from git
        """
        diff = await utils.execute('git diff')
        if not diff:
            return await utils.execute('git status')
        if not files:
            files = ('-a',)
        files = list(files)
        files.append('-m')
        files.append('"%s"' % (msg or 'commit from agile release manager'))
        return await utils.execute('git commit %s' % ' '.join(files))

    async def push(self):
        """Push to current branch
        """
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
