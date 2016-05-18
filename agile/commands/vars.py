from .. import utils


class Vars(utils.AgileApp):
    """Set context variables
    """
    description = 'Run arbitrary commands on the shell'

    async def __call__(self, name, config, options):
        self.context[name] = config['value']

    def as_dict(self, cfg, entry):
        return super().as_dict({'value': cfg}, entry)
