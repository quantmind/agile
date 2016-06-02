from .. import core


class Shell(core.AgileCommand):
    """Run shell commands
    """
    description = 'Run arbitrary commands on the shell'

    async def __call__(self, name, config, options):
        results = await self.shell(**config)
        if results:
            result = results if len(results) > 1 else results[0]
            self.app.context[name] = result
