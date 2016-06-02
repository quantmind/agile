import tests


class TestDocs(tests.AgileTest):

    async def test_doc(self):
        app = await self.app(docs='json')
        self.assertTrue(app.cfg.docs)
