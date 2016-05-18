import tests


class TestS3(tests.AgileTest):
    config = 'tests/configs/release.json'

    async def test_skip_upload(self):
        app = self.app(tasks=["upload"], config_file=self.config)
        self.assertFalse(app.cfg.push)
        await app.agile()
