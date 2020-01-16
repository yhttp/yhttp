
from easycli import Root, Argument


class Main(Root):
    __completion__ = True
    __arguments__ = []

    def __init__(self, application):
        self.application = application
        self.__help__ = '%s command line interface.' % application.name
        self.__arguments__.extend(self.application.cliarguments)
        super().__init__()

    def _execute_subcommand(self, args):
        args.application = self.application
        super()._execute_subcommand(args)

