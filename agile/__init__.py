"""Python toolkit for building, managing releases and issue tracking"""
from .version import get_version


VERSION = (0, 4, 0, 'alpha', 0)
__version__ = get_version(VERSION, __file__)
