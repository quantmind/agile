from pulsar import ImproperlyConfigured

from .. import utils
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

    def commits(self, **data):
        """Get a list of commits
        """
        return self.get_list('%s/commits' % self, Commit, **data)

    def commit(self, data):
        return Commit(self, data)

    def issues(self, **data):
        """Get a list of pull requests
        """
        return self.get_list('%s/pulls' % self, Issue, **data)

    def issue(self, data):
        return Issue(self, data)

    def pulls(self, **data):
        """Get a list of pull requests
        """
        return self.get_list('%s/pulls' % self, Pull, **data)

    def pull(self, data):
        return Pull(self, data)

    # Releases
    def releases(self, **data):
        """A github release object
        """
        return self.get_list('%s/releases' % self, Release, **data)

    def release(self, data):
        return Release(self, data)

    async def latest_release(self):
        """Get the latest release of this repo
        """
        url = '%s/releases/latest' % self
        response = await self.http.get(url, auth=self.auth)
        if response.status_code == 200:
            return Release(self, response.json())
        elif response.status_code == 404:
            self.logger.warning('No Github releases')
        else:
            response.raise_for_status()

    async def create_release(self, release):
        """Create a new release
        """
        url = '%s/releases' % self
        response = await self.http.post(url, json=release, auth=self.auth)
        response.raise_for_status()
        return Release(self, response.json())

    async def validate_tag(self, tag_name, prefix=None):
        """Validate ``tag_name`` with the latest tag from github

        If ``tag_name`` is a valid candidate, return the latest tag from github
        """
        new_version = utils.semantic_version(tag_name)
        current = await self.latest_release()
        if current:
            tag_name = current['tag_name']
            if prefix:
                tag_name = tag_name[len(prefix):]
            tag_name = utils.semantic_version(tag_name)
            if tag_name >= new_version:
                what = 'equal to' if tag_name == new_version else 'older than'
                raise ImproperlyConfigured('Your local version "%s" is %s '
                                           'the current github version "%s".\n'
                                           'Bump the local version to '
                                           'continue.' %
                                           (str(new_version), what,
                                            str(tag_name)))
        return current

    async def label(self, name, color, update=True):
        """Create or update a label
        """
        url = '%s/labels' % self
        data = dict(name=name, color=color)
        response = await self.http.post(url, json=data, auth=self.auth)
        if response.status_code == 201:
            return True
        elif update:
            url = '%s/%s' % (url, name)
            response = await self.http.patch(url, json=data, auth=self.auth)
        response.raise_for_status()
