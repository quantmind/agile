import tests

from agile.utils import ShellError
from agile.git import Git


class TestGitCommands(tests.AgileTest):

    async def test_branch(self):
        git = await Git.create()
        branch = await git.branch()
        self.assertTrue(branch)

    async def test_add_fail(self):
        git = await Git.create()
        with self.assertRaises(ShellError) as exc:
            await git.add('xaxa')
        self.assertEqual(str(exc.exception),
                         "fatal: pathspec 'xaxa' did not match any files")

    async def test_rm_fail(self):
        git = await Git.create()
        with self.assertRaises(ShellError) as exc:
            await git.rm('xaxa')
        self.assertEqual(str(exc.exception),
                         "fatal: pathspec 'xaxa' did not match any files")
