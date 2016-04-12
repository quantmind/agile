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

    async def test_commits(self):
        repo = self.repo
        commits = await repo.commits()
        self.assertTrue(commits)
        self.assertTrue(len(commits) <= 100)
        commit = commits[0]
        self.assertEqual(commit.client, repo)
        self.assertEqual(commit.id, commit['sha'])
        self.assertTrue(commit.id in commit.api_url)

    async def test_releases(self):
        repo = self.repo
        releases = await repo.releases()
        self.assertTrue(releases)
        self.assertTrue(len(releases) <= 100)
        release = releases[0]
        self.assertEqual(release.client, repo)
        self.assertEqual(release.id, release['id'])
        self.assertTrue(str(release.id) in release.api_url)

    async def test_latest_release(self):
        repo = self.repo
        release = await repo.latest_release()
        self.assertTrue(release)
        self.assertEqual(release.id, release['id'])

    async def test_upload_file(self):
        repo = self.repo
        release = await repo.latest_release()
        assets = await release.assets(limit=0)
        filename = os.path.basename(__file__)
        # Check if the filename is available
        for asset in assets:
            if asset['name'] == filename:
                self.assertEqual(asset.api_url, asset['url'])
                await asset.delete()
                await asyncio.sleep(1)
                break
        asset = await release.upload(__file__, 'text/plain')
        self.assertTrue(asset)
        self.assertTrue(asset.id)
        self.assertEqual(asset.id, asset['id'])
        self.assertEqual(asset['content_type'], 'text/plain')
        # Now delete the asset
        await asset.delete()
