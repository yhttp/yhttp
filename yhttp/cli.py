import sys
from wsgiref.simple_server import make_server

from easycli import Root, Argument, SubCommand


DEFAULT_ADDRESS = '8080'


class Serve(SubCommand):
    __command__ = 'serve'
    __aliases__ = ['s']
    __arguments__ = [
        Argument(
            '-b', '--bind',
            default=DEFAULT_ADDRESS,
            metavar='{HOST:}PORT',
            help='Bind Address. default: %s' % DEFAULT_ADDRESS
        ),
        Argument(
            '-C',
            '--directory',
            default='.',
            help='Change to this path before starting, default is: `.`'
        )
    ]

    def __call__(self, args):
        host, port = args.bind.split(':')\
            if ':' in args.bind else ('', args.bind)

        args.application.configure_extensions()
        httpd = make_server(host, int(port), args.application)
        print(f'Demo server started http://{host}:{port}')
        httpd.serve_forever()


class Main(Root):
    __completion__ = True
    __arguments__ = [
        Argument(
            '-c', '--configuration-file',
            metavar="FILE",
            dest='configurationfile',
            help='Configuration file',
        ),
        Serve,
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

