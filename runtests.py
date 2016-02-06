#!/usr/bin/env python
import sys
import os

from pulsar.apps.test import TestSuite


def run():
    args = sys.argv
    if '--coveralls' in args:
        import agile as mod
        from pulsar.utils.path import Path
        from pulsar.apps.test.cov import coveralls

        repo_token = None
        strip_dirs = [Path(mod.__file__).parent.parent, os.getcwd()]
        if os.path.isfile('.coveralls-repo-token'):
            with open('.coveralls-repo-token') as f:
                repo_token = f.read().strip()
        coveralls(strip_dirs=strip_dirs, repo_token=repo_token)
        sys.exit(0)
    # Run the test suite
    #
    TestSuite(description='Agile test suite',
              modules=['tests'],
              test_timeout=30).start()


if __name__ == '__main__':
    run()
