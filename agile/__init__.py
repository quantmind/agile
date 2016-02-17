"""Python toolkit for building, managing releases and issue tracking
"""
import os

VERSION = (0, 3, 0, 'final', 0)
__author__ = 'Luca Sbardella'
__contact__ = "luca@quantmind.com"
CLASSIFIERS = ['Development Status :: 3 - Alpha',
               'Intended Audience :: Developers',
               'License :: OSI Approved :: BSD License',
               'Operating System :: OS Independent',
               'Programming Language :: Python',
               'Programming Language :: Python :: 3',
               'Programming Language :: Python :: 3.4',
               'Programming Language :: Python :: 3.5',
               'Topic :: Utilities',
               'Topic :: Software Development :: Libraries :: Python Modules']
__version__ = '.'.join((str(v) for v in VERSION))

if os.environ.get('agile_setup') != 'yes':
    from pulsar.utils.version import get_version
    from . import commands   # noqa
    from .app import AgileManager

    __version__ = version = get_version(VERSION, __file__)
    __all__ = ['AgileManager']
