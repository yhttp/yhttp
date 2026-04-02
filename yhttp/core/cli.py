import os
import time
import sys
import subprocess
from wsgiref.simple_server import make_server

from .fswatcher import FSWatcher
from easycli import Root, Argument, SubCommand


DEFAULT_ADDRESS = '8080'


class Serve(SubCommand):  # pragma: no cover
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
            '-d', '--delay',
            metavar='MILISECONDS',
            default=1000,
            type=int,
            help='Delay before starting the server in miliseconds. this '
                 'option is only effective when `--subprocess` is specified. '
                 'default: 1000.'
        ),
        Argument(
            '-s', '--subprocess',
            metavar='CMD',
            default=[],
            action='append',
            dest='subprocesses',
            help='Command to execute as a subprocess, this option can be '
                 'specified multiple times. Note: this options is independent '
                 'from `--watch-*` options.'
        ),
        Argument(
            '-W', '--watch-directories',
            metavar='PATTERN',
            action='append',
            default=[],
            dest='watching_directories',
            help='Wildcard pattern to watch directories for changes and '
                 'restart the server. this option can be specified multiple '
                 'times.'
        ),
        Argument(
            '-w', '--watch-files',
            metavar='PATTERN',
            action='append',
            default=[],
            dest='watching_files',
            help='Wildcard pattern to watch files for changes and restart the '
                  'server. this option can be specified multiple times.'
        ),
        Argument(
            '--watch-excludedirectory',
            metavar='PATTERN',
            action='append',
            default=[],
            dest='exclude_watchingdirectories',
            help='Wildcard pattern to exclude directori(es) from being '
                 'watched. this option can be specified multiple times.'
        ),
        Argument(
            '--watch-excludefile',
            metavar='PATTERN',
            action='append',
            default=[],
            dest='exclude_watchingfiles',
            help='Wildcard pattern to exclude file(s) from being watched. '
                 'this option can be specified multiple times.'
        ),
        Argument(
            '--watch-timeout',
            metavar='MILISECONDS',
            default=1000,
            type=int,
            help='Watcher timeout, default: 1000'
        ),
    ]

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.subprocesses = []

    def _start(self, app, host, port):  # pragma: no cover
        app.ready()
        httpd = make_server(host, port, app)
        print(f'Development server started: http://{host}:{port}')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("CTRL+C pressed.")
        finally:
            app.shutdown()

    def _subprocess_serve(self, host, port):
        cmd = [sys.argv[0], 'serve', '--bind', f'{host}:{port}']
        return subprocess.Popen(cmd)

    def _serve(self, args):
        host, port = args.bind.split(':')\
            if ':' in args.bind else ('localhost', args.bind)

        if (not args.watching_directories) and (not args.watching_files):
            # simply start the server in the main process
            return self._start(args.application, host, int(port))

        watcher = FSWatcher(
            directories=args.watching_directories,
            files=args.watching_files,
            excludefiles=args.exclude_watchingfiles,
            excludedirectories=args.exclude_watchingdirectories,
        )
        try:
            sp = self._subprocess_serve(host, port)
            watcher.start()
            while True:
                changes = watcher.wait(args.watch_timeout)
                if not changes:
                    continue

                print(f'Filesystem has been changed: {",".join(changes)}, '
                      'restarting...')
                sp.terminate()
                sp.wait()
                sp = self._subprocess_serve(host, port)
        finally:
            watcher.stop()
            watcher.close()
            if sp and sp.returncode:
                sp.kill()
                sp.wait()

    def _subprocess_run(self, command):
        sp = subprocess.Popen(command, shell=True)
        self.subprocesses.append(sp)

    def _subprocess_killall(self):
        for sp in self.subprocesses:
            sp.terminate()
            sp.wait()

    def __call__(self, args):  # pragma: no cover
        try:
            if args.subprocesses:
                for sp in args.subprocesses:
                    self._subprocess_run(sp)

                if args.delay:
                    time.sleep(args.delay / 1000)

            self._serve(args)
        except KeyboardInterrupt:
            print('\nInterrupted by user: (CTRL+C)', file=sys.stdout)

        finally:
            self._subprocess_killall()


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
            '-C', '--directory',
            default='.',
            help='Change to this path before starting, default is: `.`'
        ),
        Argument(
            '-O', '--option',
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
