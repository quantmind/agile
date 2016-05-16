import tests
import io

from agile import utils


class StreamCounter(io.StringIO):
    count = 0

    def write(self, text):
        self.count += 1
        super().write(text)


class TestUtils(tests.AgileTest):

    async def test_execute(self):
        text = await utils.execute('ls')
        self.assertTrue(text)
        self.assertTrue('requirements.txt' in text)

    async def test_execute_interactive(self):
        stdout = StreamCounter()
        stderr = StreamCounter()
        text = await utils.execute('ls',
                                   interactive=True,
                                   stdout=stdout,
                                   stderr=stderr)
        self.assertFalse(text)
        self.assertTrue(stdout.count > 1)
        stdout.seek(0)
        text = stdout.read()
        self.assertTrue('requirements.txt' in text)

    def test_version(self):
        self.assertEqual(utils.semantic_version('x.y.z.t.f'), '1.2.3')
