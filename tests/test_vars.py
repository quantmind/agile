import tests


class TestPython(tests.AgileTest):
    config_file = 'tests/configs/python.json'

    async def test_simple(self):
        executor = await self.executor(tasks=["variables"])
        await executor.run()
        self.assertEqual(executor.context['random'], 50)
