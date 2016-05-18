from pulsar import as_coroutine
from pulsar.utils.importer import module_attribute

from .. import utils


class Python(utils.AgileApp):
    description = 'Run a python function from the same application domain'

    async def __call__(self, name, config, options):
        function = config.get('function')
        if not function:
            raise utils.AgileError('function path not specified')
        result = module_attribute(function)
        if hasattr(result, '__call__'):
            result = await as_coroutine(result(self))
        if result:
            self.context[name] = result

    def as_dict(self, cfg, entry):
        if isinstance(cfg, str):
            cfg = {'function': cfg}
        return super().as_dict(cfg, entry)
