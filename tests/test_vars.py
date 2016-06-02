import tests


class TestPython(tests.AgileTest):
    config_file = 'tests/configs/python.json'

    async def test_simple(self):
        app = await self.app(tasks=["variables"])
        await app()
        self.assertEqual(app.context['random'], 50)
