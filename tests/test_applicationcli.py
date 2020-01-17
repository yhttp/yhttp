import tempfile

from yhttp import Application
from easycli import SubCommand
from bddcli import Application as CLIApplication, Given, stdout, \
    status, stderr, when


class Foo(SubCommand):
    __command__ = 'foo'

    def __call__(self, args):
        assert args.application is app
        print(app.settings.title)


app = Application()
app.settings.merge('title: foo')
app.cliarguments.append(Foo)


def test_applicationcli_default():
    cliapp = CLIApplication('foo', 'tests.test_applicationcli:app.climain')
    with Given(cliapp, '--help'):
        assert status == 0

        when('foo')
        assert status == 0
        assert stdout == 'foo\n'

        with tempfile.NamedTemporaryFile() as f:
            f.write(b'title: bar')
            f.flush()
            when(f'--configuration-file {f.name} foo')
            assert status == 0
            assert stdout == 'bar\n'

