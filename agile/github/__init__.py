import logging

from pulsar.apps.http import HttpClient

from ..utils import get_auth
from .repo import GitRepo


class GithubApi:

    def __init__(self, auth=None, http=None):
        if not http:
            http = HttpClient(headers=[('Content-Type', 'application/json')])
        self.auth = auth or get_auth()
        self.http = http
        self.logger = logging.getLogger('agile.github')

    @property
    def api_url(self):
        return 'https://api.github.com'

    def repo(self, repo_path):
        return GitRepo(self, repo_path)
