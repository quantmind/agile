"""Tools for managing releases and issue tracking
"""
import os

VERSION = (0, 1, 0, 'final', 0)
__author__ = 'Luca Sbardella'
__contact__ = "luca@quantmind.com"


if os.environ.get('agile_setup') != 'yes':
    from pulsar.utils.version import get_version

    __version__ = version = get_version(VERSION, __file__)
