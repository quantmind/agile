from pulsar import ImproperlyConfigured

from ..utils import semantic_version
from .components import Commit, Pull, Issue, Release, Component


class GitRepo(Component):
    """Github repository endpoints
    """
    def __init__(self, client, repo_path):
        super().__init__(client)
        self.repo_path = repo_path

    @property
    def api_url(self):
        return '%s/repos/%s' % (self.client, self.repo_path)

    def commit(self, sha):
        """A github commit object
        """
        return Commit(self, sha)

    def issue(self, number):
        """A github issue object
        """
        return Issue(self, number)

    def pull(self, number):
        """A github pull request object
        """
        return Pull(self, number)

    def release(self, rid):
        """A github release object
        """
        return Release(self, rid)

    async def latest_release(self):
        """Get the latest release of this repo
        """
        url = '%s/releases/latest' % self
        self.logger.info('Check current Github release from %s', url)
        response = await self.http.get(url, auth=self.auth)
        if response.status_code == 200:
            data = response.json()
            current = data['tag_name']
            self.logger.info('Current Github release %s created %s by %s',
                             current, data['created_at'],
                             data['author']['login'])
            return data
        elif response.status_code == 404:
            self.logger.warning('No Github releases')
        else:
            response.raise_for_status()

    async def validate_tag(self, tag_name, prefix=None):
        """Validate ``tag_name`` with the latest tag from github

        If ``tag_name`` is a valid candidate, return the latest tag from github
        """
        new_version = semantic_version(tag_name)
        current = await self.latest_release()
        if current:
            tag_name = current['tag_name']
            if prefix:
                tag_name = tag_name[len(prefix):]
            tag_name = semantic_version(tag_name)
            if tag_name >= new_version:
                what = 'equal to' if tag_name == new_version else 'older than'
                raise ImproperlyConfigured('Your local version "%s" is %s '
                                           'the current github version "%s".\n'
                                           'Bump the local version to '
                                           'continue.' %
                                           (str(new_version), what,
                                            str(tag_name)))
        return current

    async def create_release(self, release):
        """Create a new release
        """
        url = '%s/releases' % self
        response = await self.http.post(url, data=release, auth=self.auth)
        response.raise_for_status()
        return response.json()

    async def label(self, name, color, update=True):
        """Create or update a label
        """
        url = '%s/labels' % self
        data = dict(name=name, color=color)
        response = await self.http.post(url, data=data, auth=self.auth)
        if response.status_code == 201:
            return True
        elif update:
            url = '%s/%s' % (url, name)
            response = await self.http.patch(url, data=data, auth=self.auth)
        response.raise_for_status()

    def commits(self, **data):
        """Get a list of commits
        """
        return self.get_list('%s/commits' % self, **data)

    def pulls(self, **data):
        """Get a list of pull requests
        """
        return self.get_list('%s/pulls' % self, **data)
