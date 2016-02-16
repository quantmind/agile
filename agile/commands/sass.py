from ..utils import AgileApp, as_dict, execute


class Sass(AgileApp):
    """Run SASS command

    To create css bundles
    """
    description = 'Compile scss files using SASS'

    def __call__(self, name, config, options):
        files = as_dict(config.get('files'), 'missing `files` entry')
        command = self.render(options.get('command', 'sass'))
        # TODO: we need a more general algorithm for node_modules really!
        node_modules = 'node_modules'
        args = ''
        if node_modules in command:
            args = ' --include-path %s' % node_modules
        for target, src in files.items():
            cmd = '%s%s %s %s' % (command, args, src, target)
            self.logger.info('executing sass:%s - %s', name, cmd)
            text = yield from execute(cmd)
            if text:
                self.logger.debug(text, extra=dict(color=False))
