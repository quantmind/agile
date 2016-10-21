from .. import core


class Vars(core.AgileCommand):
    """Set context variables
    """
    description = 'Set variables in the context'
    always = True

    async def run(self, name, config, options):
        self.context[name] = config['value']

    def as_dict(self, cfg, entry):
        return super().as_dict({'value': cfg}, entry)
