import tests

from agile import utils


class TestUtils(tests.AgileTest):

    async def test_execute(self):
        text = await utils.execute('ls')
        self.assertTrue(text)
        self.assertTrue('requirements.txt' in text)

    def test_version(self):
        self.assertEqual(utils.semantic_version('x.y.z.t.f'), '1.2.3')
