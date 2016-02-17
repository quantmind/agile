import logging

from pulsar import ImproperlyConfigured
from pulsar.apps.http import HttpClient

from ..utils import get_auth
from .repo import GitRepo


class GithubApi:

    def __init__(self, auth=None, http=None):
        if not http:
            http = HttpClient(headers=[('Content-Type', 'application/json')])
        self.logger = logging.getLogger('agile.github')
        self.http = http
        try:
            self.auth = auth or get_auth()
        except ImproperlyConfigured as exc:
            self.logger.warning(str(exc))
            self.auth = None

    @property
    def api_url(self):
        return 'https://api.github.com'

    def __repr__(self):
        return self.api_url
    __str__ = __repr__

    def repo(self, repo_path):
        return GitRepo(self, repo_path)
