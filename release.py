import os

from agile import AgileManager


version_file = os.path.join(os.path.dirname(__file__), 'agile', '__init__.py')


if __name__ == '__main__':
    AgileManager(config='release.py').start()
