import tests

from agile.utils import execute


class TestUtils(tests.AgileTest):

    def test_execute(self):
        text = yield from execute('ls')
        self.assertTrue(text)
        self.assertTrue('runtests.py' in text)
