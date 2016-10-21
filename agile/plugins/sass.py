import asyncio

from .. import core


class Sass(core.AgileCommand):
    """Run SASS command

    To create css bundles
    """
    description = 'Compile scss files using SASS'

    async def __call__(self, name, config, options):
        files = self.as_dict(config.get('files'), 'missing `files` entry')
        command = self.render(options.get('executable', 'sass'))
        # TODO: we need a more general algorithm for node_modules really!
        node_modules = 'node_modules'
        args = ''
        if node_modules in command:
            args = ' --include-path %s' % node_modules

        with_items = self.with_items(config)
        if with_items is None:
            with_items = ['']

        coros = []
        for item in with_items:
            for target, src in files.items():
                coros.append(self._sass(
                    command, target, src, args,
                    'css', item))
                coros.append(self._sass(
                    command, target, src, args,
                    'min.css --output-style compressed', item))

        await asyncio.gather(*coros)

    async def _sass(self, command, target, src, args, end, item):
        context = self.new_context(item=item)
        target = self.render(target, context)
        src = self.render(src, context)
        if target.endswith('.css'):
            target = target[:-4]
        #
        cmd = '%s%s %s %s.%s' % (command, args, src, target, end)
        self.logger.info(cmd)
        self.log_execute(await self.execute(cmd))
