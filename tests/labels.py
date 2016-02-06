import tests


class TestLabels(tests.AgileTest):

    def test_label(self):
        app = self.app(labels=True)
        self.assertTrue(app.cfg.labels)
