import tests


class TestApp(tests.AgileTest):
    config = 'tests/configs/python.json'

    async def test_task(self):
        app = self.app(config_file=self.config)
        self.assertFalse(app.cfg.push)
        self.assertEqual(app.eval('cfg.push'), False)
