from yhttp import Application
from easycli import SubCommand
from bddcli import Application as CLIApplication, Given, stdout, \
    status, stderr, when


class Foo(SubCommand):
    __command__ = 'foo'

    def __call__(self, args):
        assert args.application is app
        print('foo')


app = Application()
app.cliarguments.append(Foo)


def test_applicationcli_default():
    cliapp = CLIApplication('foo', 'tests.test_applicationcli:app.climain')
    with Given(cliapp, '--help'):
        assert status == 0

        when('foo')
        assert stdout == 'foo\n'

