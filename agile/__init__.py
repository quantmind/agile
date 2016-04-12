"""Python toolkit for building, managing releases and issue tracking
"""
import os

from .version import get_version


VERSION = (0, 4, 0, 'alpha', 0)
__version__ = get_version(VERSION, __file__)


if os.environ.get('package_info') != 'agile':

    from . import commands          # noqa
    from .app import AgileManager   # noqa
