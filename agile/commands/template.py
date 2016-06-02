import os

from .. import core


class Template(core.AgileCommand):
    description = 'Render a template into a new file'

    async def __call__(self, name, cfg, options):
        src = cfg.get('src')
        if not isinstance(src, str):
            raise self.error('src should be a string')
        dest = cfg.get('dest')
        if not isinstance(dest, str):
            raise self.error('dest should be a string')
        with_items = self.with_items(cfg)
        if with_items is None:
            with_items = ['']

        if not os.path.isfile(src):
            raise self.error('src %s not a valid file' % src)
        with open(src, 'r') as file:
            src = file.read()

        for item in with_items:
            self._render(src, dest, item)

    def _render(self, src, dest, item):
        context = self.context(item=item)
        src = self.render(src, context)
        dest = self.render(dest, context)
        with open(dest, 'w') as file:
            file.write(src)
        self.logger.info('Created %s' % dest)
