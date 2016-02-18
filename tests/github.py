import tests


class TestGithubApi(tests.AgileTest):

    def test_doc(self):
        app = self.app(docs='json')
        self.assertTrue(app.cfg.docs)
