import os
import json

from pulsar import ImproperlyConfigured

from ..utils import AgileApp


class Labels(AgileApp):
    description = 'Set labels in github issues'

    def can_run(self):
        return self.cfg.labels

    def __call__(self):
        label_file = os.path.join(self.app.releases_path, 'labels.json')
        if not label_file:
            raise ImproperlyConfigured('No label file %s' % label_file)
        repos = json.load(label_file)
        # loop through repos and get all labels
        for repo in repos['repos']:
            yield from self._labels(repo, repos['labels'])

    def _labels(self, repo, labels):
        pass
