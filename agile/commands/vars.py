from .. import core


class Vars(core.AgileCommand):
    """Set context variables
    """
    description = 'Run arbitrary commands on the shell'

    async def __call__(self, name, config, options):
        self.app.context[name] = config['value']

    def as_dict(self, cfg, entry):
        return super().as_dict({'value': cfg}, entry)
