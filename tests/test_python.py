import tests

import agile


def test_function(cmd):
    return 'OK'


class TestPython(tests.AgileTest):
    config = 'tests/configs/python.json'

    async def test_task(self):
        app = self.app(tasks=["test"], config_file=self.config)
        self.assertEqual(app.cfg.tasks, ["test"])
        await app.agile()
        self.assertEqual(app.context['test1'], 'OK')

    async def test_task2(self):
        app = self.app(tasks=["version"], config_file=self.config)
        await app.agile()
        self.assertEqual(app.context['agile_version'], agile.__version__)
