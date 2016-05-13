#!/usr/bin/env python3
import sys
import os

from setuptools import setup, find_packages

import agile


def read(name):
    filename = os.path.join(os.path.dirname(__file__), name)
    with open(filename) as fp:
        return fp.read()


def requirements(name):
    install_requires = []
    dependency_links = []

    for line in read(name).split('\n'):
        if line.startswith('-e '):
            link = line[3:].strip()
            if link == '.':
                continue
            dependency_links.append(link)
            line = link.split('=')[1]
        line = line.strip()
        if line:
            install_requires.append(line)

    return install_requires, dependency_links


meta = dict(
    version=agile.__version__,
    description=agile.__doc__,
    name='pulsar-agile',
    author='Luca Sbardella',
    author_email="luca@quantmind.com",
    maintainer_email="luca@quantmind.com",
    license="BSD",
    packages=find_packages(include=['agile', 'agile.*']),
    long_description=read('README.rst'),
    url='https://github.com/quantmind/pulsar-agile',
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements('requirements.txt')[0],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'agile':
        from agile.app import AgileManager
        AgileManager(description='Release manager for pulsar-agile',
                     argv=sys.argv[2:]).start()
    else:
        setup(**meta)
