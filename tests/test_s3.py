import tests


class TestS3(tests.AgileTest):

    async def test_skip_upload(self):
        app = await self.executor(tasks=["upload"])
        self.assertFalse(app.cfg.push)
        await app.run()
