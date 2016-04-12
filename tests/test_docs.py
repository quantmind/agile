import tests


class TestDocs(tests.AgileTest):

    def test_doc(self):
        app = self.app(docs='json')
        self.assertTrue(app.cfg.docs)
