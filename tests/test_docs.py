import tests


class TestDocs(tests.AgileTest):

    async def test_doc(self):
        app = await self.executor(docs='json')
        self.assertTrue(app.cfg.docs)
