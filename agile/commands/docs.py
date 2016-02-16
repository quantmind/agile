import os
from importlib import import_module

from pulsar import ImproperlyConfigured, validate_dict

from cloud import aws

from ..utils import AgileSetting, AgileApp, execute


class DocsSetting(AgileSetting):
    name = "docs"
    flags = ['--docs']
    nargs = '?'
    default = ''
    const = 'json'
    desc = "Compile documentation"


class DocsBucket(AgileSetting):
    name = "docs_bucket"
    flags = ['--docs-bucket']
    default = ''
    desc = "AWS bucket where to store docs"


class AWSconfig(AgileSetting):
    name = "aws_config"
    validator = validate_dict
    default = dict(region_name='us-east-1')
    desc = "AWS configuration dictionary"


content_types = {'fjson': 'application/json',
                 'inv': 'text/plain'}


class Docs(AgileApp):
    """Requires a valid sphinx installation
    """
    description = 'Compile sphinx docs and upload them to aws'

    def __call__(self, name, config, options):
        path = os.path.join(self.app.repo_path, 'docs')
        if not os.path.isdir(path):
            raise ImproperlyConfigured('path "%s" missing' % path)
        os.chdir(path)
        try:
            text = yield from execute('make', self.cfg.docs)
        finally:
            os.chdir(self.app.repo_path)
        self.logger.info(text)

        if self.cfg.push:
            yield from self.upload()

    def upload(self):
        """Upload documentation to amazon s3
        """
        if not self.cfg.docs_bucket:
            raise ImproperlyConfigured('Please specify the "docs_bucket" '
                                       'in your config file')
        docs = self.cfg.docs
        path = os.path.join(self.app.repo_path, 'docs', '_build', docs)
        if not os.path.isdir(path):
            raise ImproperlyConfigured('path "%s" missing' % path)
        self.logger.info('Docs at "%s"', path)
        mod = import_module(self.cfg.app_module)
        version = mod.__version__
        name = mod.__name__
        url = '%s/%s' % (name, version)
        if docs != 'html':
            url = '%s/%s' % (docs, url)
        self.logger.info('Preparing to upload to "%s/%s"',
                         self.cfg.docs_bucket, url)
        aws_config = self.config['docs'].get('aws_config', {})
        s3 = aws.AsyncioBotocore('s3', http_session=self.gitapi.http,
                                 **aws_config)
        yield from s3.upload_folder(self.cfg.docs_bucket, path, url,
                                    skip=['environment.pickle', 'last_build'],
                                    content_types=content_types)
