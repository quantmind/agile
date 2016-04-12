from pulsar import ImproperlyConfigured
from pulsar.apps.test import AsyncAssert

import tests


class TestGithubApp(tests.GithubMix, tests.AgileTest):
    config = 'tests/configs/release.json'

    async def test_bad_task(self):
        app = self.app(tasks=["badtask"], config_file=self.config,
                       gitapi=self.github)
        self.assertEqual(app.cfg.tasks, ["badtask"])
        await AsyncAssert(self).assertRaises(ImproperlyConfigured, app.agile)

    async def test_task(self):
        app = self.app(tasks=["releasepy"], config_file=self.config,
                       gitapi=self.github)
        self.assertEqual(app.cfg.tasks, ["releasepy"])
        await app.agile()
