import os
import shutil

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

    async def test_release_notes(self):
        try:
            app = self.app(tasks=["releasepy"], config_file=self.config,
                           gitapi=self.github)
            self.assertEqual(app.cfg.tasks, ["releasepy"])
            await app.agile()
            self.assertTrue(os.path.isfile('test_release_note.md'))
            self.assertFalse(os.path.isdir('tests/history'))
            await app.agile()
            self.assertTrue(os.path.isdir('tests/history'))
        finally:
            if os.path.isdir('tests/history'):
                shutil.rmtree('tests/history')
            if os.path.isfile('test_release_note.md'):
                os.remove('test_release_note.md')
