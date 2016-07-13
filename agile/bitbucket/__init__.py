import os
import logging
import configparser

from pulsar.apps.http import HttpClient

from .. import utils


class BitBucketApi:

    def __init__(self, auth=None, http=None):
        if not http:
            http = HttpClient()
        self.logger = logging.getLogger('agile.github')
        self.http = http
        try:
            self.auth = auth or get_auth()
        except utils.AgileError as exc:
            self.logger.warning(str(exc))
            self.auth = None


def get_auth():
    """Return a tuple for authenticating a user

    If not successful raise ``AgileError``.
    """
    home = os.path.expanduser("~")
    config = os.path.join(home, '.gitconfig')
    if not os.path.isfile(config):
        raise utils.AgileError('.gitconfig file not available in %s'
                               % home)

    parser = configparser.ConfigParser()
    parser.read(config)
    if 'user' in parser:
        user = parser['user']
        if 'username' not in user:
            raise utils.AgileError('Specify username in %s user '
                                   'section' % config)
        if 'token' not in user:
            raise utils.AgileError('Specify token in %s user section'
                                   % config)
        return user['username'], user['token']
    else:
        raise utils.AgileError('No user section in %s' % config)
