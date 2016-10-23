from .. import core


class Tasks(core.AgileCommand):
    """Combine several commands together and run them
    """
    description = 'Combine commands together and run them'

    async def run(self, name, cfg, options):
        commands = self.as_list(cfg.get('command'), 'missing command entry')
        result = await core.execute_commands(self, commands, options)
        return result
