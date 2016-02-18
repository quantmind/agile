# Github

The githup app is a great tool for managing releases on github. A typical
configuration for a python project ``pyapp``:
```json
{
    "github": {
        "pyapp": {
            "python_module": "pyapp",
            "version": "pyapp.__version__",
            "release-notes": "docs/source/history"
        }
    }
}
```
Available parameters::
```
tag_prefix = ''
```
Prefix to apply to the semantic version, for example setting ``tag_prefix = 'v'``
would generate github tags such as ``v1.3.2``.
```
release_notes = 'some/path
```
Path to the release note history. If not given, no release notes are generated.
```
version = {{ package.version }}
```
Where to obtain the version for the new release. The above example works for
a node package for example. For a python package One would combine
```
python_module = 'module_name'
```
If available, the entry is a release for a python module, with
```
version = mudule_name.__version__
```
for example.
