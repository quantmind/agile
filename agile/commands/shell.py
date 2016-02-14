from pulsar import ImproperlyConfigured

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
            text = yield from execute(com)
            self.logger.debug('executed shell:%s -> %s', name, com)
            if text:
                results.append(text)
        text = ' && '.join(results)
        if text:
            self.context[name] = text
            self.logger.info('executed shell:%s -> %s', name, text)
        else:
            self.logger.info('executed shell:%s', name)
