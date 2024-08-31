import os
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
    ]

    def __call__(self, args):  # pragma: no cover
        """the no cover pragma was set, because the coverae meassurement in
        subprocess is so complicated, but this function is covered by
        test_builtincli.py.
        """
        host, port = args.bind.split(':')\
            if ':' in args.bind else ('localhost', args.bind)

        args.application.ready()
        httpd = make_server(host, int(port), args.application)
        print(f'Demo server started http://{host}:{port}')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("CTRL+C pressed.")
            args.application.shutdown()


class Main(Root):
    __completion__ = True
    __arguments__ = [
        Argument(
            '-c', '--configuration-file',
            metavar="FILE",
            dest='configurationfile',
            help='Configuration file',
        ),
        Argument(
            '-C',
            '--directory',
            default='.',
            help='Change to this path before starting, default is: `.`'
        ),
        Argument(
            '-O',
            '--option',
            action='append',
            default=[],
            help='Set a configutation entry: -O foo.bar.baz=\'qux\'. this '
                 'argument can passed multiple times.'
        ),
        Serve,
    ]

    def __init__(self, application):
        if application.version:
            self.__arguments__.append(
                Argument('--version', action='store_true')
            )

        self.application = application
        self.__help__ = f'{sys.argv[0]} command line interface.'
        self.__arguments__.extend(self.application.cliarguments)
        super().__init__()

    def _execute_subcommand(self, args):
        args.application = self.application

        if args.directory != '.':
            os.chdir(args.directory)

        if args.configurationfile:
            self.application.settings.loadfile(args.configurationfile)

        for o in args.option:
            try:
                key, value = o.split('=')
            except ValueError:
                print(f'Invalid option: -O/--option {o}', file=sys.stderr)
                self._parser.print_help()
                return 1

            yml = ''
            indent = 0
            for k in key.split('.'):
                if indent:
                    yml += f'\n{indent * " "}{k}:'
                else:
                    yml += f'{k}:'

                indent += 2

            yml += f' {value}'
            self.application.settings.merge(yml)

        return super()._execute_subcommand(args)

    def __call__(self, args):
        if self.application.version and args.version:
            print(self.application.version)
            return

        self._parser.print_help()
