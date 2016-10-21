from asyncio import gather

from .. import core


class Shell(core.AgileCommand):
    """Run shell commands
    """
    description = 'Run arbitrary commands on the shell'

    async def run(self, name, cfg, options):
        with_items = self.with_items(cfg)
        if with_items is None:
            with_items = ['']

        results = []
        for item in with_items:
            context = self.new_context(item=item)
            results.append(self.shell(context=context, **cfg))

        results = await gather(*results)
        if len(results) == 1:
            results = results[0]
            if results and len(results) == 1:
                results = results[0]

        self.context[name] = results
