import os
import shutil

import tests


class TestGithubApp(tests.GithubMix, tests.AgileTest):

    async def test_bad_task(self):
        agile = await self.executor(["badtask"])
        self.assertEqual(agile.cfg.tasks, ["badtask"])
        self.assertEqual(await agile.run(), 2)

    async def __test_release_notes(self):
        try:
            agile = await self.executor(["releasepy"])
            self.assertEqual(agile.cfg.tasks, ["releasepy"])
            self.assertEqual(await agile.run(), 0)
            self.assertTrue(os.path.isfile('test_release_note.md'))
            self.assertFalse(os.path.isdir('tests/history'))
            self.assertEqual(await agile.run(), 0)
            self.assertTrue(os.path.isdir('tests/history'))
        finally:
            if os.path.isdir('tests/history'):
                shutil.rmtree('tests/history')
            if os.path.isfile('test_release_note.md'):
                os.remove('test_release_note.md')
