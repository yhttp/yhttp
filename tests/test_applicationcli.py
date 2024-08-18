import tempfile

from bddcli import Application as CLIApplication, Given, stdout, status, when
from easycli import SubCommand

from yhttp.core import Application


class Foo(SubCommand):
    __command__ = 'foo'

    def __call__(self, args):
        assert args.application is app
        print(app.settings.title)
        if app.settings.title == 'bar':
            return 73  # The best number ever, as Sheldon says.

        return 0


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
            assert status == 73
            assert stdout == 'bar\n'
