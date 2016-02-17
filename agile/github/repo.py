from pulsar import ImproperlyConfigured

from ..utils import semantic_version


class Component:

    def __init__(self, client):
        self.client = client

    def __repr__(self):
        return self.api_url
    __str__ = __repr__

    def __getattr__(self, name):
        return getattr(self.client, name)


class GitRepo(Component):
    """Github repository endpoints
    """
    def __init__(self, client, repo_path):
        super().__init__(client)
        self.repo_path = repo_path

    @property
    def api_url(self):
        return '%s/repos/%s' % (self.client, self.repo_path)

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
            return semantic_version(current)
        elif response.status_code == 404:
            self.logger.warning('No Github releases')
        else:
            response.raise_for_status()

    async def validate_tag(self, tag_name):
        """Validate ``tag_name`` with the latest tag from github
        """
        new_version = semantic_version(tag_name)
        version = list(new_version)
        version.append('final')
        version.append(0)
        current = await self.latest_release()
        if current and current >= new_version:
            what = 'equal to' if current == new_version else 'older than'
            raise ImproperlyConfigured('Your local version "%s" is %s '
                                       'the current github version "%s".' %
                                       (str(new_version), what, str(current)))
        return tuple(version)

    async def create_tag(self, release):
        """Create a new tag
        """
        url = '%s/releases' % self
        response = await self.http.post(url, data=release, auth=self.auth)
        response.raise_for_status()
        result = response.json()
        return result['tag_name']

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
