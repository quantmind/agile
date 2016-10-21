import os
import asyncio
import glob

from .. import core


class S3(core.AgileCommand):
    description = 'Upload files to S3'

    async def run(self, name, config, options):
        try:
            from cloud import aws
        except ImportError:
            raise self.error(
                'S3 command requires pulsar-cloud, install it with pip')
        opts = dict(options)
        opts.update(config)

        files = self.as_dict(opts.pop('files', None),
                             'No files given, must be a dictionary')
        bucket = opts.pop('bucket', None)
        if not bucket:
            raise self.error('No bucket entry found. '
                             'Specify it in the s3.options dictionary')
        s3 = aws.AsyncioBotocore('s3', http_session=self.gitapi.http,
                                 **opts)
        requests = []
        for src, target in files.items():
            src = self.render(src)
            target = self.render(target)
            if not target.endswith('/'):
                raise self.error('s3 targets should end with a slash /')

            if os.path.isdir(src):
                requests.append(s3.upload_folder(bucket, src, target))

            else:
                for filename in glob.glob(src):
                    requests.append(self._upload_file(s3, bucket,
                                                      filename, target))
        await asyncio.gather(*requests)

    async def _upload_file(self, s3, bucket, filename, target):
        result = await s3.upload_file(bucket, filename, uploadpath=target)
        if 'Key' in result:
            key = result['Key']
            self.logger.debug('Uploaded %s to %s', filename, key)
        else:
            self.logger.error('Could not upload %s', filename)
