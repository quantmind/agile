import pulsar

from agile.app import AgileManager

from lux.core import LuxCommand


class Command(LuxCommand):
    help = "Run agile commands for development"

    def __call__(self, argv):
        app = self.app
        server = self.pulsar_app(argv, AgileManager)

        if not server.logger:   # pragma    nocover
            app._started = server()
            pulsar.arbiter().start()
