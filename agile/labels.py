import json

from .git import Github


def labels(repos=None, labels=None):
    if not repos:
        repos = json.load('agile/labels.json')
    if not labels:
        labels = json.load('agile/labels.json')
    # loop through repos and get all labels
    for repo in repos:
        pass


