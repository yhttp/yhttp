from bddcli import Application as CLIApplication, Given, stdout, status, \
    when, stderr
from easycli import SubCommand

from yhttp.core import Application, logging


logger = logging.getlogger(__name__)


class Foo(SubCommand):
    __command__ = 'foo'

    def __call__(self, args):
        logger.debug('foo')
        logger.info('foo')
        logger.warning('foo')
        logger.error('foo')
        logger.critical('foo')
        print(f'verbosity: {args.verbosity}')


app = Application('0.1.0', 'foo')
app.cliarguments.append(Foo)


def test_logging(bddcli_bootpatch):
    cliapp = CLIApplication('foo', f'{__name__}:app.climain')
    freezetime = \
        'import time_machine;' \
        'time_machine.travel("2012-02-14 16:00:01", tick=False).start()\n'

    with bddcli_bootpatch(freezetime), Given(cliapp, 'foo'):
        assert stderr == ''
        assert status == 0
        assert stdout == (
            '2012-02-14 16:00:01.000 WARNING tests.test_logging: foo\n'
            '2012-02-14 16:00:01.000 ERROR tests.test_logging: foo\n'
            '2012-02-14 16:00:01.000 CRITICAL tests.test_logging: foo\n'
            'verbosity: 30\n'
        )

        when('-v foo')
        assert stderr == ''
        assert status == 0
        assert stdout == (
            '2012-02-14 16:00:01.000 INFO tests.test_logging: foo\n'
            '2012-02-14 16:00:01.000 WARNING tests.test_logging: foo\n'
            '2012-02-14 16:00:01.000 ERROR tests.test_logging: foo\n'
            '2012-02-14 16:00:01.000 CRITICAL tests.test_logging: foo\n'
            'verbosity: 20\n'
        )

        when('-vv foo')
        assert stderr == ''
        assert status == 0
        assert stdout == (
            '2012-02-14 16:00:01.000 DEBUG tests.test_logging: foo\n'
            '2012-02-14 16:00:01.000 INFO tests.test_logging: foo\n'
            '2012-02-14 16:00:01.000 WARNING tests.test_logging: foo\n'
            '2012-02-14 16:00:01.000 ERROR tests.test_logging: foo\n'
            '2012-02-14 16:00:01.000 CRITICAL tests.test_logging: foo\n'
            'verbosity: 10\n'
        )

        when('-q foo')
        assert stderr == ''
        assert status == 0
        assert stdout == (
            '2012-02-14 16:00:01.000 ERROR tests.test_logging: foo\n'
            '2012-02-14 16:00:01.000 CRITICAL tests.test_logging: foo\n'
            'verbosity: 40\n'
        )

        when('-qq foo')
        assert stderr == ''
        assert status == 0
        assert stdout == (
            '2012-02-14 16:00:01.000 CRITICAL tests.test_logging: foo\n'
            'verbosity: 50\n'
        )

        when('-qqq foo')
        assert stderr == ''
        assert status == 0
        assert stdout == 'verbosity: 60\n'

        when('-vvv foo')
        assert stderr.endswith(
            'foo: error: option -v only allowed up to twice\n'
        )

        when('-qqqq foo')
        assert stderr.endswith(
            'foo: error: option -q only allowed up to 3 times\n'
        )

        when('-q -v foo')
        assert stderr.endswith(
            'foo: error: argument -v/--verbose: not allowed with argument '
            '-q/--quiet\n'
        )
