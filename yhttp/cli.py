
from easycli import Root, Argument


class Main(Root):
    __completion__ = True
    __arguments__ = []

    def __init__(self, application):
        self.application = application
        self.__help__ = '%s command line interface.' % application.name
        self.__arguments__.extend(self.application.__cliarguments__)
        super().__init__()

