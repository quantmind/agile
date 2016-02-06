import unittest

import agile


class AgileTest(unittest.TestCase):

    @classmethod
    def app(cls, **kwargs):
        return agile.AgileManager(**kwargs)
