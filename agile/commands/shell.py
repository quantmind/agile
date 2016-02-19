from .. import utils


class Shell(utils.AgileApp):
    """Run shell commands
    """
    description = 'Run arbitrary commands on the shell'

    async def __call__(self, name, config, options):
        results = await self.shell(name, config.get('command'))
        if results:
            self.context[name] = results if len(results) > 1 else results[0]
