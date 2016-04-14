:Badges: |license|  |pyversions| |status| |downloads|
:Master CI: |master-build| |coverage-master|
:Downloads: http://pypi.python.org/pypi/pulsar-agile
:Source: https://github.com/quantmind/pulsar-agile
:Mailing list: `google user group`_
:Design by: `Quantmind`_ and `Luca Sbardella`_
:Platforms: Linux, OSX, Windows. Python 3.5 and above
:Keywords: git, github, python, aws, release, documentation

.. |pyversions| image:: https://img.shields.io/pypi/pyversions/pulsar-agile.svg
  :target: https://pypi.python.org/pypi/pulsar-agile
.. |license| image:: https://img.shields.io/pypi/l/pulsar-agile.svg
  :target: https://pypi.python.org/pypi/pulsar-agile
.. |status| image:: https://img.shields.io/pypi/status/pulsar-agile.svg
  :target: https://pypi.python.org/pypi/v
.. |downloads| image:: https://img.shields.io/pypi/dd/pulsar-agile.svg
  :target: https://pypi.python.org/pypi/pulsar-agile
.. |master-build| image:: https://travis-ci.org/quantmind/pulsar-agile.svg?branch=master
  :target: https://travis-ci.org/quantmind/pulsar-agile
.. |coverage-master| image:: https://coveralls.io/repos/github/quantmind/pulsar-agile/badge.svg?branch=master
  :target: https://coveralls.io/github/quantmind/pulsar-agile?branch=master

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

**Check tasks available**::

  python agileplay.py -l

**Release dry run**::

  python agileplay.py release

**Release push**::

  python agileplay.py release --push


Testing
-----------

To run unit tests, create a ``test_config.py`` file alongside this file and add
the following two entries:

.. code:: python

    import os

    os.environ['GITHUB_USERNAME'] = "<username for token>"
    os.environ['GITHUB_TOKEN'] = "<generate one from https://github.com/settings/tokens>"
    os.environ['GITHUB_TEST_REPO'] = "<username>/<reponame>"


.. _`Luca Sbardella`: http://lucasbardella.com
.. _`Quantmind`: http://quantmind.com
.. _`google user group`: https://groups.google.com/forum/?fromgroups#!forum/python-pulsar
.. _agileplay.py: https://github.com/quantmind/pulsar-agile/blob/master/agileplay.py
.. _agile.json: https://github.com/quantmind/pulsar-agile/blob/master/agile.json
