import tests


class TestShell(tests.AgileTest):
    config_file = 'tests/configs/shell1.json'

    async def test_no_tasks(self):
        app = await self.app()
        self.assertEqual(app.cfg.tasks, [])

    async def test_task(self):
        app = await self.app(["show"])
        self.assertEqual(app.cfg.tasks, ["show"])
        await self.wait.assertEqual(app(), 0)
