#!/usr/bin/env python3
import os
from setuptools import setup, find_packages

try:
    import pulsar     # noqa
except ImportError:
    os.environ['agile_setup'] = 'yes'

mod = __import__('agile')
this_dir = os.path.dirname(__file__)
req_path = os.path.join(this_dir, 'requirements.txt')
install_requires = []
dependency_links = []


def parse_requirements(path):
    with open(path, 'r', encoding='utf-8') as fp:
        for line in fp:
            if line[:3] == '-r ':
                parse_requirements(os.path.join(this_dir, line[3:].strip()))
                continue
            elif line.startswith('-e '):
                link = line[3:].strip()
                if link == '.':
                    continue
                dependency_links.append(link)
                line = link.split('=')[1]
            install_requires.append(line.strip())

parse_requirements(req_path)


if __name__ == '__main__':

    setup(
        name='git-agile',
        version=mod.__version__,
        packages=find_packages(exclude=['tests', 'tests.*']),
        description="Tools for agile development on github",
        url='https://github.com/quantmind/agile',
        include_package_data=True,
        zip_safe=False,
        install_requires=install_requires,
        dependency_links=dependency_links
    )
