import tests


class TestPython(tests.AgileTest):
    config = 'tests/configs/python.json'

    async def test_simple(self):
        app = self.app(tasks=["variables"], config_file=self.config)
        await app.agile()
        self.assertEqual(app.context['random'], 50)
