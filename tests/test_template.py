import os
import shutil

import tests


class TestTemplate(tests.AgileTest):

    async def test_template_wildcard(self):
        app = await self.executor(["template1"])
        self.assertEqual(app.cfg.tasks, ["template1"])
        try:
            await app.run()
            self.assertTrue(os.path.isdir('tests/templates-dest'))
        finally:
            if os.path.isdir('tests/templates-dest'):
                shutil.rmtree('tests/templates-dest')
