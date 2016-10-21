import os
import unittest
from unittest import skipUnless

from agile.github import GithubApi
from agile.github.releases import Releases
from agile.app import AgileManager
from agile.utils import AgileError
from agile import utils

EXECUTE_MOCKS = {}

USERNAME = os.environ.get('GITHUB_USERNAME', '')
TOKEN = os.environ.get('GITHUB_TOKEN', '')
REPO = os.environ.get('GITHUB_TEST_REPO', '')

original_semantic_version = utils.semantic_version
original_execute = utils.execute
original_validate_tag = Releases.validate_tag


def semantic_version(version):
    try:
        original_semantic_version(version)
    except AgileError:
        pass
    return '1.2.3'


async def validate_tag(self, tag_name, prefix=None):
    try:
        await original_validate_tag(self, tag_name, prefix)
    except AgileError:
        pass
    return await self.latest()


async def execute(command, **kw):
    if command in EXECUTE_MOCKS:
        return EXECUTE_MOCKS[command]
    else:
        return await original_execute(command, **kw)

utils.semantic_version = semantic_version
utils.execute = execute

Releases.validate_tag = validate_tag


class AgileTest(unittest.TestCase):
    config_file = 'tests/configs/release.json'
    auth = None

    @classmethod
    def executor(cls, tasks=None, config_file=None, **kwargs):
        config_file = config_file or cls.config_file
        app = AgileManager(tasks=tasks, config_file=config_file, **kwargs)
        return app.executor(auth=cls.auth)


@skipUnless(TOKEN and USERNAME and REPO,
            'Github token, username and test repo must be available')
class GithubMix:
    auth = (USERNAME, TOKEN)

    @classmethod
    def setUpClass(cls):
        cls.github = GithubApi(auth=cls.auth)
        cls.repo = cls.github.repo(REPO)

    @classmethod
    def tearDownClass(cls):
        return cls.github.http.close()
