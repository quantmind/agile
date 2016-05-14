import tests


def test_function(app):
    return 'OK'


class TestPython(tests.AgileTest):
    config = 'tests/configs/python.json'

    async def test_task(self):
        app = self.app(tasks=["test"], config_file=self.config)
        self.assertEqual(app.cfg.tasks, ["test"])
        await app.agile()
        self.assertEqual(app.context['test1'], 'OK')
