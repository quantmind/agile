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

**ALPHA - USE IT WITH EXTRA CARE**

========
Agile
========

Toolkit for agile development with python, git, github and aws.

Usage
--------


Create the agileplay.py_ script inside of your repository and create the
agile.json_ file along side.

Available commands to configure are:

* **docs**: Compile sphinx docs and upload them to aws
* **httpcopy**: Copy remote files to local ones via Http
* **labels**: Set labels in github issues
* **release**: Make a new release
* **sass**: Compile scss files using SASS
* **shell**: Run arbitrary commands on the shell

When running tasks, the logging level is by default set to info. For a more
verbose logging pass ``--log-level agile.debug``.

Dry run::

    python release.py release


Push::

    python agileplay.py release --push


.. _`Luca Sbardella`: http://lucasbardella.com
.. _`Quantmind`: http://quantmind.com
.. _`google user group`: https://groups.google.com/forum/?fromgroups#!forum/python-pulsar
.. _agileplay.py: https://github.com/quantmind/git-agile/blob/master/agileplay.py
.. _agile.json: https://github.com/quantmind/git-agile/blob/master/agile.json
