import os
from importlib import import_module

from pulsar import ImproperlyConfigured

from cloud import aws

from .. import utils


content_types = {'fjson': 'application/json',
                 'inv': 'text/plain'}


class Docs(utils.AgileApp):
    """Requires a valid sphinx installation
    """
    description = 'Compile sphinx docs and upload them to aws'

    async def __call__(self, name, config, options):
        path = os.path.join(self.app.repo_path, 'docs')
        if not os.path.isdir(path):
            raise ImproperlyConfigured('path "%s" missing' % path)
        os.chdir(path)
        try:
            text = await utils.execute('make', self.cfg.docs)
        finally:
            os.chdir(self.app.repo_path)
        self.logger.info(text)

        if self.cfg.push:
            await self.upload()

    async def upload(self):
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
        await s3.upload_folder(self.cfg.docs_bucket, path, url,
                               skip=['environment.pickle', 'last_build'],
                               content_types=content_types)
