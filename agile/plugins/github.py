"""Agile app for managing releases
"""
import os
from datetime import date
import glob
import asyncio

from dateutil import parser

from pulsar.utils.html import capfirst

from .. import core


class RemoveRelease(core.AgileSetting):
    name = "remove_release"
    flags = ['--remove-release']
    nargs = "?"
    const = 'current'
    desc = "Remove a release from github"


close_issue = set((
    'close',
    'closes',
    'closed',
    'fix',
    'fixes',
    'fixed',
    'resolve',
    'resolves',
    'resolved'
))


class Github(core.AgileCommand):
    """Create Github releases.

    Without the ``--commit`` or ``--push`` flags nothing is committed
    or pushed to the remote repository
    """
    description = 'Create a new release in github'
    actions = frozenset(('shell', 'upload'))

    async def run(self, name, config, options):
        git = self.git
        gitapi = self.gitapi
        release_notes_file = config.get('release_notes_file',
                                        'release-notes.md')
        release = {}
        opts = dict(options)
        opts.update(config)
        # repo api object
        repo = gitapi.repo(git.repo_path)
        #
        # Get the version to release and validate
        version = opts.get('version')
        if not version:
            raise self.error('"version" not specified in github.%s '
                             'dictionary' % name)
        version = self.render(version)

        if self.cfg.remove_release:
            if self.cfg.remove_release != 'current':
                version = self.cfg.remove_release
            await self.remove_release(version)
            return

        tag_prefix = opts.get('tag_prefix', '')
        current = await repo.releases.validate_tag(version, tag_prefix) or {}
        release['tag_name'] = version
        #
        # Release notes
        location = opts.get('release_notes')
        if location:
            note_file = os.path.join(self.repo_path, release_notes_file)
            if os.path.isfile(note_file):
                with open(note_file, 'r') as file:
                    release['body'] = file.read().strip()
                await self.write_notes(location, release)
            else:
                self.logger.info('Create release notes from commits &'
                                 ' pull requests')
                release['body'] = await self.get_notes(repo, current)
                with open(note_file, 'w') as file:
                    file.write(release['body'])
                # Extit so that the release manager can edit the file
                # before releasing
                return self.logger.info('Created new %s file' % note_file)
        #
        # Commit or Push
        if self.cfg.commit or self.cfg.push:
            #
            # Create the tar or zip file
            dist = self.as_dict(opts.get('dist', {}),
                                "dist entry should be a dictionary")
            for name, value in dist.items():
                if name not in self.actions:
                    raise self.error('No such action "%s"' % name)
            #
            version = '%s%s' % (tag_prefix, version)
            release['tag_name'] = version
            self.logger.info('Commit changes')
            self.log_execute(await git.commit(msg='Release %s' % version))
            #
            # Push to github and create tag
            if self.cfg.push:
                self.logger.info('Push changes')
                self.log_execute(await git.push())
                self.logger.info('Pause for two second before creating a tag')
                await asyncio.sleep(2)
                self.logger.info('Creating a new tag %s', version)
                release = await repo.releases.create(release)
                self.logger.info('Congratulation, the new release %s is out',
                                 release['tag_name'])

    async def remove_release(self, tag):
        repo = self.gitapi.repo(self.git.repo_path)
        self.logger.info('Remove release %s from github', tag)
        try:
            await repo.releases.delete(tag=tag)
        except Exception as exc:
            response = getattr(exc, 'response', None)
            if response and response.status_code == 404:
                self.logger.warning('Release with tag %s not available', tag)
            else:
                raise
        # Remove tag
        await self.git.tags_remove(tag)

    async def upload(self, name, src, release=None, **kw):
        if release:
            tag = release['tag_name']
            rel = self.gitapi.repo(self.git.repo_path).release(release['id'])
            for src in self.as_list(src):
                src = self.render(src)
                for filename in glob.glob(src):
                    self.logger.info('Uploading %s to release %s',
                                     filename, tag)
                    await rel.upload(filename)

    async def get_notes(self, repo, current):
        """Fetch release notes from github
        """
        created_at = current.get('created_at')
        notes = []
        notes.extend(await self._from_commits(repo, created_at))
        notes.extend(await self._from_pull_requests(repo, created_at))

        sections = {}
        for _, section, body in reversed(sorted(notes, key=lambda s: s[0])):
            if section not in sections:
                sections[section] = []
            sections[section].append(body)

        body = []
        for title in sorted(sections):
            if title:
                body.append('### %s' % capfirst(title))
            for entry in sections[title]:
                if not entry.startswith('* '):
                    entry = '* %s' % entry
                body.append(entry)
            body.append('')
        return '\n'.join(body)

    async def add_note(self, repo, notes, message, dte, eid, entry):
        """Add a not to the list of notes if a release note key is found
        """
        key = '#release-note'
        index = message.find(key)

        if index == -1:
            substitutes = {}
            bits = message.split()
            for msg, bit in zip(bits[:-1], bits[1:]):
                if bit.startswith('#') and msg.lower() in close_issue:
                    try:
                        number = int(bit[1:])
                    except ValueError:
                        continue
                    if bit not in substitutes:
                        try:
                            issue = await repo.issue(number).get()
                        except Exception:
                            continue
                        substitutes[bit] = issue['html_url']
            if substitutes:
                for name, url in substitutes.items():
                    message = message.replace(name, '[%s](%s)' % (name, url))
                notes.append((dte, '', message))
        else:
            index1 = index + len(key)
            if len(message) > index1 and message[index1] == '=':
                section = message[index1+1:].split()[0]
                key = '%s=%s' % (key, section)
            else:
                section = ''
            body = message.replace(key, '').strip()
            if body:
                body = body[:1].upper() + body[1:]
                body = '%s [%s](%s)' % (body, eid, entry['html_url'])
                notes.append((dte, section.lower(), body))

    async def write_notes(self, location, release):
        dt = date.today().strftime('%Y-%b-%d')
        version = release['tag_name']
        title = '## Ver. %s' % version
        body = ['%s - %s' % (title, dt), '']
        body.extend(release['body'].strip().splitlines())
        bits = version.split('.')
        bits[2] = 'md'
        filename = os.path.join(location, '.'.join(bits))
        if not os.path.isdir(location):
            os.makedirs(location)
        add_file = True
        if os.path.isfile(filename):
            # We need to add the file
            add_file = False
            with open(filename, 'r') as file:
                lines = file.read().strip().splitlines()
            lines = self._remove_notes(lines, title)
            body.extend(('', ''))
            body.extend(lines)

        with open(filename, 'w') as file:
            file.write('\n'.join(body))

        self.logger.info('Added release notes to %s', filename)

        if add_file:
            self.logger.info('Add %s to repository', filename)
            await self.git.add(filename)

    def _remove_notes(self, lines, title):
        # We need to remove the previous notes
        remove = False
        for line in lines:
            if line.startswith(title):
                remove = True
            elif line.startswith('## '):
                remove = False
            if not remove:
                yield line

    async def _from_commits(self, repo, created_at=None):
        #
        # Collect notes from commits
        notes = []
        for entry in await repo.commits.get_list(since=created_at):
            commit = entry['commit']
            dte = parser.parse(commit['committer']['date'])
            eid = entry['sha'][:7]
            message = commit['message']
            await self.add_note(repo, notes, message, dte, eid, entry)
            if commit['comment_count']:
                for comment in await repo.commits.comments(entry):
                    message = comment['body']
                    await self.add_note(repo, notes, message, dte, eid, entry)
        return notes

    async def _from_pull_requests(self, repo, created_at=None):
        #
        # Collect notes from pull requests
        callback = check_update(created_at) if created_at else None

        pulls = await repo.pulls.get_list(callback=callback,
                                          state='closed',
                                          sort='updated',
                                          direction='desc')
        notes = []
        for entry in pulls:
            message = entry['body']
            dte = parser.parse(entry['closed_at'])
            eid = '#%d' % entry['number']
            await self.add_note(repo, notes, message, dte, eid, entry)
            comments = await repo.issues.comments(entry)
            for comment in comments:
                message = comment['body']
                await self.add_note(repo, notes, message, dte, eid, entry)
        return notes


class check_update:
    """Filter pull requests
    """
    def __init__(self, since):
        self.since = parser.parse(since)

    def __call__(self, pulls):
        new_pulls = []
        for pull in pulls:
            dte = parser.parse(pull['updated_at'])
            if dte > self.since:
                new_pulls.append(pull)
        return new_pulls
