import os
import json

from pulsar import ImproperlyConfigured

from .utils import (passthrough, change_version, write_notes,
                    AgileSetting, AgileApp)


class Commit(AgileSetting):
    name = "labels"
    flags = ['--labels']
    action = "store_true"
    default = False
    desc = "update labels"


class Labels(AgileApp):

    def __call__(self):
        if not self.cfg.labels:
            return
        label_file = os.path.join(self.releases_path, 'labels.json')
        if not label_file:
            raise ImproperlyConfigured('No label file %s' % label_file)
        repos = json.load(label_file)
        # loop through repos and get all labels
        for repo in repos['repos']:
            yield from self._labels(repo, repos['labels'])

    def _labels(self, repo, labels):
        pass
