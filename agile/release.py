'''Pulsar app for creating releases. Used by pulsar.
'''
import os
import json
import logging

import pulsar
from pulsar import ImproperlyConfigured, as_coroutine

from .utils import (passthrough, change_version, write_notes,
                    AgileSetting, AgileApp)


class ReleaseSetting(AgileSetting):
    name = "release"
    flags = ['--release']
    action = "store_true"
    default = False
    desc = "Create a new release"


class Commit(AgileSetting):
    name = "commit"
    flags = ['--commit']
    action = "store_true"
    default = False
    desc = "Commit changes"


class BeforeCommit(AgileSetting):
    name = "before_commit"
    validator = pulsar.validate_callable(2)
    type = "callable"
    default = staticmethod(passthrough)
    desc = """\
        Callback invoked before committing changes
        """


class WriteNotes(AgileSetting):
    name = "write_notes"
    validator = pulsar.validate_callable(2)
    type = "callable"
    default = staticmethod(write_notes)
    desc = """\
        Write release notes
        """


class Push(AgileSetting):
    name = "push"
    flags = ['--push']
    action = "store_true"
    default = False
    desc = "Push changes to origin"


class VersionFile(AgileSetting):
    name = "version_file"
    default = ""
    desc = """\
        Python module containing the VERSION = ... line
        """


class ChangeVersion(AgileSetting):
    name = "change_version"
    validator = pulsar.validate_callable(2)
    type = "callable"
    default = staticmethod(change_version)
    desc = """\
        Change the version number in the code
        """

exclude = set(pulsar.Config().settings)
exclude.difference_update(('config', 'loglevel', 'debug'))


class Release(AgileApp):

    def __call__(self):
        git = self.git
        gitapi = self.gitapi

        release_json = os.path.join(self.app.releases_path, 'release.json')

        if not os.path.isfile(release_json):
            raise ImproperlyConfigured('%s file not available' % release_json)

        # Load release config and notes
        with open(release_json, 'r') as file:
            release = json.load(file)

        with open(self.app.note_file, 'r') as file:
            release['body'] = file.read().strip()

        yield from as_coroutine(self.cfg.before_commit(self, release))

        # Validate new tag and write the new version
        tag_name = release['tag_name']
        repo = gitapi.repo(git.repo_path)
        version = yield from repo.validate_tag(tag_name)
        self.logger.info('Bump to version %s', version)
        self.cfg.change_version(self, tuple(version))
        #
        if self.cfg.commit or self.cfg.push:
            #
            # Add release note to the changelog
            yield from as_coroutine(self.cfg.write_notes(self, release))
            self.logger.info('Commit changes')
            result = yield from git.commit(msg='Release %s' % tag_name)
            self.logger.info(result)
            if self.cfg.push:
                self.logger.info('Push changes changes')
                result = yield from git.push()
                self.logger.info(result)

                self.logger.info('Creating a new tag %s' % tag_name)
                tag = yield from repo.create_tag(release)
                self.logger.info('Congratulation, the new release %s is out',
                                 tag)

        return True
