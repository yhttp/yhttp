from yhttp import Application
from easycli import SubCommand
from bddcli import Application as CLIApplication, Given, stdout, \
    status, stderr, when

class Foo(SubCommand):
    __command__ = 'foo'

    def __call__(self, args):
        print('foo')


app = Application()
app.__cliarguments__.append(Foo)
main = app.climain


def test_applicationcli_default():
    cliapp = CLIApplication('foo', 'tests.test_applicationcli:main')
    with Given(cliapp, '--help'):
        print(stderr)
        assert status == 0

        when('foo')
        assert stdout == 'foo\n'

