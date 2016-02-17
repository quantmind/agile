import tests

from agile.utils import execute


class TestUtils(tests.AgileTest):

    async def test_execute(self):
        text = await execute('ls')
        self.assertTrue(text)
        self.assertTrue('runtests.py' in text)
