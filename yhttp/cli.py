import sys

from easycli import Root, Argument


class Main(Root):
    __completion__ = True
    __arguments__ = [
        Argument(
            '-c', '--configuration-file',
            metavar="FILE",
            dest='configurationfile',
            help='Configuration file',
        ),
    ]

    def __init__(self, application):
        self.application = application
        self.__help__ = f'{sys.argv[0]} command line interface.'
        self.__arguments__.extend(self.application.cliarguments)
        super().__init__()

    def _execute_subcommand(self, args):
        args.application = self.application
        if args.configurationfile:
            self.application.settings.loadfile(args.configurationfile)

        super()._execute_subcommand(args)

