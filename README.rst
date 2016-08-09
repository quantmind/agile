**Toolkit for agile development with python, git, github, docker and aws**

:Badges: |license|  |pyversions| |status| |pypiversion|
:Master CI: |master-build| |coverage-master|
:Downloads: http://pypi.python.org/pypi/pulsar-agile
:Source: https://github.com/quantmind/pulsar-agile
:Mailing list: `google user group`_
:Design by: `Quantmind`_ and `Luca Sbardella`_
:Platforms: Linux, OSX, Windows. Python 3.5 and above
:Keywords: git, github, python, aws, release, documentation


.. |pypiversion| image:: https://badge.fury.io/py/pulsar-agile.svg
  :target: https://pypi.python.org/pypi/pulsar-agile
.. |pyversions| image:: https://img.shields.io/pypi/pyversions/pulsar-agile.svg
  :target: https://pypi.python.org/pypi/pulsar-agile
.. |license| image:: https://img.shields.io/pypi/l/pulsar-agile.svg
  :target: https://pypi.python.org/pypi/pulsar-agile
.. |status| image:: https://img.shields.io/pypi/status/pulsar-agile.svg
  :target: https://pypi.python.org/pypi/pulsar-agile
.. |downloads| image:: https://img.shields.io/pypi/dd/pulsar-agile.svg
  :target: https://pypi.python.org/pypi/pulsar-agile
.. |master-build| image:: https://travis-ci.org/quantmind/pulsar-agile.svg?branch=master
  :target: https://travis-ci.org/quantmind/pulsar-agile
.. |coverage-master| image:: https://coveralls.io/repos/github/quantmind/pulsar-agile/badge.svg?branch=master
  :target: https://coveralls.io/github/quantmind/pulsar-agile?branch=master

|

.. contents:: **CONTENTS**


Install
==========

This is a python package for aiding deployment and dev-ops type operations on the local machine.
To install the package you need python 3.5 or above::

    pip install -U pulsar-agile


Setup
-------

Once installed, create the ``play.py`` script inside of your repository:

.. code:: python

    if __name__ == '__main__':
        from agile.app import AgileManager
        AgileManager(description='Release manager for my package').start()


and create the agile.json_ file along side it.

Commands
------------

Available commands to configure are:

* **docs**: Compile sphinx docs and upload them to aws
* **httpcopy**: Copy remote files to local ones via Http
* **labels**: Set labels in github issues
* **release**: Make a new release
* **sass**: Compile scss files using SASS
* **shell**: Run arbitrary commands on the shell


Usage
=========

**Check tasks available**::

  python play.py -l

**Release dry run**::

  python play.py release

**Release push**::

  python play.py release --push


Logging
----------

When running tasks, the logging level is by default set to info. For a more
verbose logging pass ``--log-level agile.debug``.

Testing
==========

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
.. _agile.json: https://github.com/quantmind/pulsar-agile/blob/master/agile.json
