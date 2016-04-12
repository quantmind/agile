import tests


class TestShell(tests.AgileTest):
    config = 'tests/configs/shell1.json'

    def test_no_tasks(self):
        app = self.app(config_file=self.config)
        self.assertEqual(app.cfg.tasks, [])

    async def test_task(self):
        app = self.app(tasks=["show"], config_file=self.config)
        self.assertEqual(app.cfg.tasks, ["show"])
        await app.agile()
