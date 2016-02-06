:Master CI: |master-build|_ |coverage-master|
:Dev CI: |dev-build|_ |coverage-dev|
:Documentation: http://pythonhosted.org/pulsar/
:Downloads: http://pypi.python.org/pypi/pulsar
:Source: https://github.com/quantmind/pulsar
:Mailing list: `google user group`_
:Design by: `Quantmind`_ and `Luca Sbardella`_
:Platforms: Linux, OSX, Windows. Python 3.4 and above
:Keywords: git, github, python, aws, release, documentation

.. |master-build| image:: https://travis-ci.org/quantmind/pulsar.svg?branch=master
.. _master-build: http://travis-ci.org/quantmind/pulsar
.. |dev-build| image:: https://travis-ci.org/quantmind/pulsar.svg?branch=dev
.. _dev-build: http://travis-ci.org/quantmind/pulsar
.. |coverage-master| image:: https://coveralls.io/repos/github/quantmind/pulsar/badge.svg?branch=master
  :target: https://coveralls.io/github/quantmind/pulsar?branch=master
.. |coverage-dev| image:: https://coveralls.io/repos/github/quantmind/pulsar/badge.svg?branch=dev
  :target: https://coveralls.io/github/quantmind/pulsar?branch=dev

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
