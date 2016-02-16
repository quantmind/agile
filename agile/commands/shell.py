from ..utils import AgileApp, as_list, execute


class Shell(AgileApp):
    """Run shell commands
    """
    description = 'Run arbitrary commands on the shell'

    def __call__(self, name, config, options):
        coms = as_list(config.get('command'), 'missing `command` entry')
        results = []
        for com in coms:
            com = self.render(com)
            self.logger.info('executing shell:%s - %s', name, com)
            text = yield from execute(com)
            if text:
                self.logger.debug('\n%s', text, extra=dict(color=False))
                results.append(text)
        if results:
            self.context[name] = results if len(results) > 1 else results[0]
