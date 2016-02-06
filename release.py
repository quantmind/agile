import os

from agile import AgileManager

app_module = 'agile'
note_file = 'docs/notes.md'
docs_bucket = 'quantmind-docs'

if __name__ == '__main__':
    AgileManager(config='release.py').start()
