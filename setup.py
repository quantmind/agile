#!/usr/bin/env python3
from setuptools import setup, find_packages

import agile_config as config


if __name__ == '__main__':

    meta = dict(
        name='pulsar-agile',
        author='Luca Sbardella',
        author_email="luca@quantmind.com",
        maintainer_email="luca@quantmind.com",
        license="BSD",
        packages=find_packages(include=['agile', 'agile.*']),
        long_description=config.read('README.rst'),
        url='https://github.com/quantmind/pulsar-agile',
        include_package_data=True,
        zip_safe=False,
        install_requires=config.requirements('requirements.txt')[0],
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Topic :: Utilities',
            'Topic :: Software Development :: Libraries :: Python Modules'
        ]
    )

    setup(**config.setup(meta, 'agile'))
