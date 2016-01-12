import json


def labels(repos=None, labels=None):
    if not repos:
        repos = json.load('agile/labels.json')
    if not labels:
        labels = json.load('agile/labels.json')
    for repo in repos:

