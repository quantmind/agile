:Master CI: |master-build|_ |coverage-master|
:Downloads: http://pypi.python.org/pypi/git-agile
:Source: https://github.com/quantmind/git-agile
:Mailing list: `google user group`_
:Design by: `Quantmind`_ and `Luca Sbardella`_
:Platforms: Linux, OSX, Windows. Python 3.4 and above
:Keywords: git, github, python, aws, release, documentation

.. |master-build| image:: https://travis-ci.org/quantmind/git-agile.svg?branch=master
.. _master-build: http://travis-ci.org/quantmind/git-agile
.. |coverage-master| image:: https://coveralls.io/repos/github/quantmind/git-agile/badge.svg?branch=master
  :target: https://coveralls.io/github/quantmind/git-agile?branch=master

========
Agile
========

Tools for agile development with git, github and aws.

Usage
--------


Create the release.py_
script inside of your repository.

Dry run::

    python release.py --release


Push::

    python release.py --release --push


.. _`Luca Sbardella`: http://lucasbardella.com
.. _`Quantmind`: http://quantmind.com
.. _`google user group`: https://groups.google.com/forum/?fromgroups#!forum/python-pulsar
.. _release.py: https://github.com/quantmind/git-agile/blob/master/release.py
