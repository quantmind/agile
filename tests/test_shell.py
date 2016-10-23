import tests


class TestShell(tests.AgileTest):
    config_file = 'tests/configs/shell1.json'

    async def test_no_tasks(self):
        app = await self.executor()
        self.assertEqual(app.cfg.tasks, [])

    async def test_task(self):
        app = await self.executor(["tasks:show"])
        self.assertEqual(app.cfg.tasks, ["tasks:show"])
        self.assertFalse(await app.run())
