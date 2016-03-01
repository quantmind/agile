from .. import utils


class Sass(utils.AgileApp):
    """Run SASS command

    To create css bundles
    """
    description = 'Compile scss files using SASS'

    async def __call__(self, name, config, options):
        files = utils.as_dict(config.get('files'), 'missing `files` entry')
        command = self.render(options.get('executable', 'sass'))
        # TODO: we need a more general algorithm for node_modules really!
        node_modules = 'node_modules'
        args = ''
        if node_modules in command:
            args = ' --include-path %s' % node_modules
        for target, src in files.items():
            if target.endswith('.css'):
                target = target[:-4]
            #
            cmd = '%s%s %s %s.css' % (command, args, src, target)
            self.logger.info('executing sass:%s - %s', name, cmd)
            self.log_execute(await utils.execute(cmd))
            #
            cmd = '%s%s %s %s.min.css --output-style compressed' % (
                command, args, src, target)
            self.logger.info('executing sass:%s - %s', name, cmd)
            self.log_execute(await utils.execute(cmd))
