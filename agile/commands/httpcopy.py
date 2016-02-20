import os
import asyncio
from urllib.parse import urlsplit

from pulsar import ImproperlyConfigured

from .. import utils


class HttpCopy(utils.AgileApp):
    description = 'Copy remote files to local ones via Http'

    async def __call__(self, name, cfg, options):
        srcs = utils.as_list(cfg.get('src'), 'missing src')
        target = cfg.get('target')
        if not target:
            raise ImproperlyConfigured('%s: target is missing' % name)
        requests = []
        for src in srcs:
            requests.append(self._http_and_copy(src, target))
        await asyncio.gather(*requests)

    async def _http_and_copy(self, src, target):
        response = await self.http.get(src)
        response.raise_for_status()
        path, target = os.path.split(target)
        if not os.path.isdir(path):
            os.makedirs(path)
        if not target:
            target = urlsplit(src).path.split('/')[-1]
        target = os.path.join(path, target)
        self.logger.info('%s => %s', src, target)
        with open(target, 'wb') as file:
            file.write(response.content)
