# Releases

We follow [Semantic Versioning](http://semver.org/) throughout this
documentation. This package can aide the release process, it is not designed to
make a release for you but it gives you a platform you can build on.

## Release script

The first thing to do is to create the ``release.py`` script along side the
``setup.py`` script of your module::
```python
from agile import AgileManager

# Name of the python module to release
app_module = 'agile'
# Release notes files
note_file = 'docs/notes.md'
# This is for uploading docs to aws (optional)
docs_bucket = 'xxxx'

if __name__ == '__main__':
    AgileManager(config='release.py').start()
```

Add a ``requirements-dev.in`` file with at least the following entries:
```
flake8
coverage
pip
pip-tools
piprot
```
Add the ``requirements.in`` with a list of requirement for the python module
which need to be released.


## Up-to-date Requirements

This is important for application rather than libraries.

Make the development requirements are up-to-date by issuing:
```
pip install -U -r requirements-dev.in
```

or if you use [pyenv](https://github.com/yyuu/pyenv) (highly recommended)
```
pyenv exec pip install -U -r requirements-dev.in
```

The repository has a ``requirements*.in`` file that lists its direct
dependencies (usually without versions).
The ``requirements*.txt`` files are frozen versions of these files
(i.e. they record the specific package versions to be used).

The [piprot](https://pypi.python.org/pypi/piprot) tool does this. You can use find to automatically locate and report on the file:
```
find . -name 'requirements*.txt' -exec piprot {} \;
```

If the requirements are up to date, no action is required; otherwise,
you'll need to update them.
To do this, run pip-compile on each ``requirements*.in`` file:
```
find . -name 'requirements*.in' -exec pip-compile {} \;
```

## Release cut

The best time to make release cuts is the middle of the week,
I like Wednesday but Thursday is also good.
The day of release cut, the RM merge all changes in the 
``master`` branch into the ``release`` branch. For example the release branch
could be ``0.4`` or any other ``<MAJOR>.<MINOR>`` combination.


## Making a repository release

The best time to make releases is the end of the week,
I like Thursday but Friday is also good.
The day before release day, the RM freezes the repositories which have
received updates and release the new versions.

To release a repository, move into the repo directory and
on the ``<MAJOR>.<MINOR>`` branch and run
```
python release.py --release
```
This won't do the release, but it will perform some sanity checks. To actually release
```
python release.py --release --push
```


## Reverse a release

If during the release cut something went wrong, you can easily reverse
the release by:

* deleting the tag in origin
```
git push origin :refs/tags/<tag_name>
```
* remove remove the draft release notes (they have become draft because the
  underlying tag has been deleted by the above command) in github.
* Delete the latest notes from where they were appended inside the release/history folder
