from pulsar import as_coroutine
from pulsar.utils.importer import module_attribute

from .. import utils


class Python(utils.AgileApp):
    """Run shell commands
    """
    description = 'Run a python function from the same application domain'

    async def __call__(self, name, config, options):
        function = config.get('function')
        if not function:
            raise utils.AgileError('function path not specified')
        func = module_attribute(function)
        result = await as_coroutine(func(self))
        if result:
            self.context[name] = result

    def as_dict(self, cfg, entry):
        if isinstance(cfg, str):
            cfg = {'function': cfg}
        return super().as_dict(cfg, entry)
