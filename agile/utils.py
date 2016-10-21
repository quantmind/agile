import sys
import asyncio
from collections import Mapping

from pulsar.utils.string import to_bytes

from jinja2 import Template


STREAM_LIMIT = 2**20


class AgileError(Exception):
    pass


class AgileExit(AgileError):
    pass


class AgileSkip(AgileError):
    pass


class ShellError(AgileError):

    def __init__(self, msg, code):
        super().__init__(msg)
        self.code = code


def render(text, context):
    template = Template(text)
    return template.render(**context)


def semantic_version(tag):
    """Get a valid semantic version for tag
    """
    try:
        version = list(map(int, tag.split('.')))
        assert len(version) == 3
        return tuple(version)
    except Exception as exc:
        raise AgileError('Could not parse "%s", please use '
                         'MAJOR.MINOR.PATCH' % tag) from exc


async def execute(command, input=None, chdir=None, interactive=False,
                  stderr=None, stdout=None, **kw):
    """Execute a shell command
    :param command: command to execute
    :param input: optional input
    :param chdir: optional directory to execute the shell command from
    :param  interactive: display output as it becomes available
    :return: the output text
    """
    stdin = asyncio.subprocess.PIPE if input is not None else None
    if chdir:
        command = 'cd %s && %s' % (chdir, command)

    proc = await asyncio.create_subprocess_shell(
        command,
        stdin=stdin,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        limit=STREAM_LIMIT
    )
    if input is not None:
        proc._feed_stdin(to_bytes(input))

    msg, err = await asyncio.gather(
        _interact(proc, 1, interactive, stdout or sys.stdout),
        _interact(proc, 2, interactive, stderr or sys.stderr)
    )
    if proc.returncode:
        msg = '%s%s' % (msg.decode('utf-8'), err.decode('utf-8'))
        raise ShellError(msg.strip(), proc.returncode)
    return msg.decode('utf-8').strip()


def skip_file(name):
    return name.startswith('.') or name.startswith('__')


def as_list(entry, msg=None):
    if entry and not isinstance(entry, list):
        entry = [entry]
    if not entry:
        raise AgileError(msg or 'Not a valid entry')
    return entry


def as_dict(entry, msg=None):
    if not isinstance(entry, Mapping):
        raise AgileError(msg or 'Not a valid entry')
    return entry


def safe(f):

    async def _(self, *args, **kwargs):
        try:
            code = await f(self, *args, **kwargs)
            return code
        except AgileError as exc:
            self.logger.error(str(exc))
            return 2
        except Exception as exc:
            self.logger.exception(str(exc))
            return 1

    return _


async def _interact(proc, fd, interactive, out):
    transport = proc._transport.get_pipe_transport(fd)
    stream = proc.stdout if fd == 1 else proc.stderr
    output = b''
    while interactive:
        line = await stream.readline()
        if not line:
            break
        out.write(line.decode('utf-8'))
    else:
        output = await stream.read()
    transport.close()
    return output
