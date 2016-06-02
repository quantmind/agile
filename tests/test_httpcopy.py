import os
import shutil

import tests


tmp = 'tests/temp'


class TestHttpCopy(tests.AgileTest):

    @classmethod
    def setUpClass(cls):
        cls.cleanUp()
        os.makedirs(tmp)

    @classmethod
    def tearDownClass(cls):
        cls.cleanUp()

    @classmethod
    def cleanUp(cls):
        if os.path.isdir(tmp):
            shutil.rmtree(tmp)

    async def test_http_copy_files(self):
        agile = await self.app(["httpfiles"])
        agile.context['tmp'] = tmp
        await self.wait.assertEqual(agile(), 0)
        self.assertTrue(os.path.isdir(tmp))
        self.assertTrue(os.path.isdir(os.path.join(tmp, 'flatly')))
        self.assertTrue(os.path.isdir(os.path.join(tmp, 'journal')))

    async def test_http_copy_error(self):
        agile = await self.app(["httpcopy-error"])
        await self.wait.assertEqual(agile(), 1)
