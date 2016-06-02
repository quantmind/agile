import tests


class TestLabels(tests.AgileTest):

    async def test_label(self):
        app = await self.app(labels=True)
        self.assertTrue(app.cfg.labels)
