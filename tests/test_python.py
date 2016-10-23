import tests

import agile


def test_function(cmd):
    return 'OK'


class TestPython(tests.AgileTest):
    config_file = 'tests/configs/python.json'

    async def test_task(self):
        app = await self.executor(["tasks:test"])
        self.assertEqual(app.cfg.tasks, ["tasks:test"])
        self.assertFalse(await app.run())
        self.assertEqual(app.context['test1'], 'OK')

    async def test_task2(self):
        app = await self.executor(["tasks:version"])
        self.assertFalse(await app.run())
        self.assertEqual(app.context['agile_version'], agile.__version__)
