import asyncio

from .. import core


class Labels(core.AgileCommand):
    description = 'Set labels in github issues'

    async def run(self, name, config, options):
        repositories = self.as_list(config.get('repositories'),
                                    'No repositories given, must be a list')
        labels = self.as_dict(config.get('labels'),
                              'No labels given, must be a dictionary mapping '
                              'names to colors')
        requests = []
        for repo in repositories:
            for name, color in labels.items():
                requests.append(self._labels(repo, name, color))
        await asyncio.gather(*requests)

    async def _labels(self, repo, name, color):
        repo = self.gitapi.repo(repo)
        if await repo.label(name, color):
            self.logger.debug('Created label "%s" @ %s', name, repo)
        else:
            self.logger.debug('Updated label "%s" @ %s', name, repo)
