import unittest

from pulsar import ImproperlyConfigured

import agile


original_semantic_version = agile.utils.semantic_version
original_validate_tag = agile.github.GitRepo.validate_tag


def semantic_version(version):
    try:
        original_semantic_version(version)
    except ImproperlyConfigured:
        pass
    return '1.2.3'


async def validate_tag(self, tag_name, prefix=None):
    try:
        await original_validate_tag(self, tag_name, prefix)
    except ImproperlyConfigured:
        pass
    current = await self.latest_release()
    return current


agile.utils.semantic_version = semantic_version

agile.github.GitRepo.validate_tag = validate_tag


class AgileTest(unittest.TestCase):

    @classmethod
    def app(cls, **kwargs):
        return agile.AgileManager(**kwargs)
