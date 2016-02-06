import os

import pulsar
from pulsar import ensure_future, ImproperlyConfigured

from .git import Git


exclude = set(pulsar.Config().settings)
exclude.difference_update(('config', 'loglevel', 'debug'))

from .utils import agile_apps, AgileSetting


class NoteFile(AgileSetting):
    name = "note_file"
    flags = ["--note-file"]
    default = 'releases/notes.md'
    desc = """\
        File with release notes
        """


class AgileManager(pulsar.Application):
    name = 'agile'
    cfg = pulsar.Config(apps=['agile'],
                        loglevel=['pulsar.error', 'info'],
                        description='Agile release manager',
                        exclude=exclude)
    git = None
    gitapi = None
    note_file = None
    releases_path = None

    def monitor_start(self, monitor, exc=None):
        cfg = self.cfg
        cfg.set('workers', 0)

    def worker_start(self, worker, exc=None):
        if not exc:
            worker._loop.call_soon(ensure_future, self._start_agile(worker))

    def _start_agile(self, worker):
        exit_code = 1
        try:
            self.git = yield from Git.create()
            self.gitapi = self.git.api()
            # Read the release note file
            path = yield from self.git.toplevel()
            self.logger.info('Repository directory %s', path)
            self.note_file = os.path.join(path, self.cfg.note_file)
            if not os.path.isfile(self.note_file):
                raise ImproperlyConfigured('%s file not available' %
                                           self.note_file)

            self.releases_path = os.path.dirname(self.note_file)
            yield from agile_apps(self)
        except ImproperlyConfigured as exc:
            self.logger.error(str(exc))
        except Exception as exc:
            self.logger.exception(str(exc))
        else:
            exit_code = None
        worker._loop.call_soon(self._exit, exit_code)

    def _exit(self, exit_code):
        pulsar.arbiter().stop(exit_code=exit_code)

    def _release(self):
        self.git = git = yield from Git.create()
        self.gitapi = gitapi = git.api()

        path = yield from git.toplevel()
        self.logger.info('Repository directory %s', path)
        # Read the release note file
        note_file = os.path.join(path, self.cfg.note_file)
        if not os.path.isfile(note_file):
            raise ImproperlyConfigured('%s file not available' % note_file)

        self.releases_path = os.path.dirname(note_file)
        release_json = os.path.join(self.releases_path, 'release.json')

        if not os.path.isfile(release_json):
            raise ImproperlyConfigured('%s file not available' % release_json)

        # Load release config and notes
        with open(release_json, 'r') as file:
            release = json.load(file)

        with open(note_file, 'r') as file:
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
