import os
import asyncio

import tests


class TestGithubApi(tests.GithubMix, tests.AgileTest):

    def test_url(self):
        repo = self.repo
        self.assertTrue(repo.api_url)
        self.assertEqual(repo.api_url,
                         '%s/repos/%s' % (self.github.api_url, tests.REPO))
        self.assertEqual(repo.client, self.github)
        self.assertEqual(repo.repo_path, tests.REPO)

    # COMMITS
    async def test_commits(self):
        repo = self.repo
        commits = await repo.commits.get_list()
        self.assertTrue(commits)
        self.assertTrue(len(commits) <= 100)
        commit = commits[0]
        self.assertTrue(commit['sha'])

    # RELEASES
    async def test_releases(self):
        repo = self.repo
        releases = await repo.releases.get_list()
        self.assertTrue(releases)
        self.assertTrue(len(releases) <= 100)

    async def test_latest_release(self):
        repo = self.repo
        release = await repo.releases.latest()
        self.assertTrue(release)

    async def test_release_by_tag(self):
        repo = self.repo
        release = await repo.releases.latest()
        self.assertTrue(release)
        bytag = await repo.releases.tag(release['tag_name'])
        self.assertEqual(bytag['id'], release['id'])

    async def __test_upload_file(self):
        repo = self.repo
        release = await repo.releases.latest()
        assets = await repo.releases.release_assets(release)
        filename = os.path.basename(__file__)
        # Check if the filename is available
        for asset in assets:
            if asset['name'] == filename:
                await repo.releases.assets.delete(asset)
                await asyncio.sleep(1)
                break
        asset = await repo.releases.upload(release, __file__, 'text/plain')
        self.assertTrue(asset)
        self.assertTrue(asset['id'])
        self.assertEqual(asset['content_type'], 'text/plain')
        # Now delete the asset
        await repo.releases.assets.delete(asset)
