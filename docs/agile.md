
# Agile Application

The agile application allow to define a set of local dev operations in a JSON file.

## github

The githup app is a great tool for managing releases on github. A typical
configuration for a python project ``pyapp``:
```json
{
    "github": {
        "pyapp": {
            "python_module": "pyapp",
            "version": "pyapp.__version__",
            "release-notes": "docs/history"
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

## httpcopy

Copy remote files to the local file system via HTTP. For example this entry in
the ``agile.json`` file specify three different download configurations:
```json
"httpcopy": {
    "flatly": {
        "src": [
            "https://bootswatch.com/flatly/_bootswatch.scss",
            "https://bootswatch.com/flatly/_variables.scss"
        ],
        "target": "scss/deps/bootswatch/"
    },
    "highlight": {
        "src": [
            "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.1.0/styles/tomorrow.min.css"
        ],
        "target": "scss/deps/highlight/"
    },
    "pace": {
        "src": [
            "https://cdnjs.cloudflare.com/ajax/libs/pace/1.0.2/themes/black/pace-theme-center-simple.css"
        ],
        "target": "scss/deps/"
    }
}
```

## python

## shell

Run shell commands asynchronously. The shell command has the following structure:
```json
{
    "shell": {
        "name1": {
            "command": "<required command or list of commands>"
            "intercative": "<optional - default is false>"
        },
        "name2": {
        }
    }
}   
```

## S3

The s3 command allow to upload a directory into an s3 location. This module
requires [pulsar-cloud][]:


    pip install pulsar-cloud
    
    
To use it add the ``s3`` entry in th ``agile.json`` file:
```json
"s3": {
    "options": {
        "bucket": "<bucket-to-upload>"
    }
    "oper1": {
        "files": {
            "<src1>": "<key-target1>"
            "<src2>": "<key-target2>"
        }
    }
}
```

[pulsar-cloud]: https://github.com/quantmind/pulsar-cloud
