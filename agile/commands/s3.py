import asyncio
import glob

from .. import utils


class S3(utils.AgileApp):
    description = 'Upload files to S3'

    async def __call__(self, name, config, options):
        try:
            from cloud import aws
        except ImportError:
            raise utils.ImproperlyConfigured(
                'S3 command requires pulsar-cloud, install with pip')
        files = utils.as_dict(config.get('files'),
                              'No files given, must be a dictionary')
        opts = dict(options)
        opts.update(config.get('options', {}))
        bucket = opts.pop('bucket', None)
        if not bucket:
            raise utils.AgileError('No bucket entry found.'
                                   'Specify it in the s3.options dictionary')
        s3 = aws.AsyncioBotocore('s3', http_session=self.gitapi.http,
                                 **opts)
        requests = []
        for src, target in files.items():
            src = self.render(src)
            target = self.render(target)
            if not target.endswith('/'):
                raise utils.AgileError('s3 targets should end with a slash /')
            for filename in glob.glob(src):
                requests.append(self._upload(s3, bucket, filename, target))
        await asyncio.gather(*requests)

    async def _upload(self, s3, bucket, filename, target):
        result = await s3.upload_file(bucket, filename, uploadpath=target)
        if 'Key' in result:
            key = result['Key']
            self.logger.debug('Uploaded %s to %s', filename, key)
        else:
            self.logger.error('Could not upload %s', filename)
