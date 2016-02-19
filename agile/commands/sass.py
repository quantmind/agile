from .. import utils


class Sass(utils.AgileApp):
    """Run SASS command

    To create css bundles
    """
    description = 'Compile scss files using SASS'

    async def __call__(self, name, config, options):
        files = utils.as_dict(config.get('files'), 'missing `files` entry')
        command = self.render(options.get('command', 'sass'))
        # TODO: we need a more general algorithm for node_modules really!
        node_modules = 'node_modules'
        args = ''
        if node_modules in command:
            args = ' --include-path %s' % node_modules
        for target, src in files.items():
            cmd = '%s%s %s %s' % (command, args, src, target)
            self.logger.info('executing sass:%s - %s', name, cmd)
            text = await utils.execute(cmd)
            if text:
                self.logger.debug(text, extra=dict(color=False))
