import os
import asyncio
from urllib.parse import urlsplit

from .. import core


class HttpCopy(core.AgileCommand):
    description = 'Copy remote files to local ones via Http'

    async def run(self, name, cfg, options):
        srcs = self.as_list(cfg.get('src'), 'missing src')
        target = cfg.get('target')
        if not target:
            raise self.error('target is missing in config dictionary')
        requests = []
        with_items = self.with_items(cfg)
        if with_items is None:
            with_items = ['']

        for item in with_items:
            for src in srcs:
                requests.append(self._http_and_copy(src, target, item))
        await asyncio.gather(*requests)

    async def _http_and_copy(self, src, target, item):
        context = self.new_context(item=item)
        src = self.render(src, context)
        target = self.render(target, context)
        response = await self.http.get(src)
        try:
            response.raise_for_status()
        except Exception:
            self.logger.error('Could not http copy %s: %s',
                              src, response.get_status())
            return
        path, target = os.path.split(target)
        if not os.path.isdir(path):
            os.makedirs(path)
        if not target:
            target = urlsplit(src).path.split('/')[-1]
        target = os.path.join(path, target)
        self.logger.info('%s => %s', src, target)
        with open(target, 'wb') as file:
            file.write(response.content)
