from .. import core
from .. import utils


class When(core.AgileAction):

    def __call__(self, agile, options):
        if 'when' in options and not self.eval(options['when']):
            raise utils.AgileSkip
