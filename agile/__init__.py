"""Python toolkit for agile release managing, building and issue tracking"""
from .version import get_version


VERSION = (0, 5, 0, 'final', 0)
__version__ = get_version(VERSION, __file__)
