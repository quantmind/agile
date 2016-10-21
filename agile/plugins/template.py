import os

from glob2 import glob

from .. import core


class Template(core.AgileCommand):
    description = 'Render a template into a new file'

    async def run(self, name, cfg, options):
        src = cfg.get('src')
        if not isinstance(src, str):
            raise self.error('src should be a string')
        dest = cfg.get('dest')
        if not isinstance(dest, str):
            raise self.error('dest should be a string')
        replace = cfg.get('replace', {})
        if not isinstance(replace, dict):
            raise self.error('`replace` should be a dictionary mapping string '
                             'targets with new values')

        with_items = self.with_items(cfg)
        if with_items is None:
            with_items = ['']

        if not os.path.isfile(src):
            src = glob(src)
            if not src:
                raise self.error('src %s not a valid file nor a group of files'
                                 % src)

        for item in with_items:
            self._render(src, dest, item, replace)

    def _render(self, src, dest, item, replace):
        context = self.new_context(item=item)
        dest = self.render(dest, context)

        is_glob = True
        if not isinstance(src, list):
            is_glob = False
            src = [src]

        for source in src:
            with open(source, 'r') as file:
                src = file.read()
            for old, new in replace.items():
                src = src.replace(old, new)
            src = self.render(src, context)
            dst = dest

            if is_glob:
                dst = os.path.join(dest, os.path.basename(source))

            dst_dir = os.path.dirname(dst)
            if not os.path.isdir(dst_dir):
                os.makedirs(dst_dir)

            with open(dst, 'w') as file:
                file.write(src)

            self.logger.info('Created %s' % dst)
