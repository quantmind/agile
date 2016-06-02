import tests


class TestApp(tests.AgileTest):
    config_file = 'tests/configs/python.json'

    async def test_task(self):
        agile = await self.app()
        self.assertTrue(agile.context)
        self.assertFalse(agile.cfg.push)
        self.assertEqual(agile.eval('cfg.push'), False)
