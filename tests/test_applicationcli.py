import os
import tempfile

from bddcli import Application as CLIApplication, Given, stdout, status, \
    when, stderr
from easycli import SubCommand

from yhttp.core import Application


class Foo(SubCommand):
    __command__ = 'foo'

    def __call__(self, args):
        assert args.application is app
        print(app.settings.title)
        if os.path.abspath(os.curdir) == '/tmp':
            print('/tmp')
        else:
            print(os.curdir)
        if app.settings.title == 'bar':
            return 73  # The best number ever, as Sheldon says.

        return 0


class Bar(SubCommand):
    __command__ = 'bar'

    def __call__(self, args):
        print(app.settings.foo.bar.baz)
        return 0


app = Application()
app.cliarguments.append(Foo)
app.cliarguments.append(Bar)
app.settings.merge('title: foo')
app.settings.merge('''
foo:
  bar:
    baz: qux
''')


def test_applicationcli():
    cliapp = CLIApplication('foo', 'tests.test_applicationcli:app.climain')
    with Given(cliapp, '--help'):
        assert status == 0

        when('foo')
        assert status == 0
        assert stdout == 'foo\n.\n'

        with tempfile.NamedTemporaryFile() as f:
            f.write(b'title: bar')
            f.flush()
            when(f'--configuration-file {f.name} foo')
            assert status == 73
            assert stdout == 'bar\n.\n'

            when('--directory /tmp foo')
            assert status == 0
            assert stdout == 'foo\n/tmp\n'

            when('--option title=\'baz\' foo')
            assert status == 0
            assert stdout == 'baz\n.\n'


def test_applicationcli_option():
    cliapp = CLIApplication('foo', 'tests.test_applicationcli:app.climain')
    with Given(cliapp, '--help'):
        assert status == 0

        when('bar')
        assert status == 0
        assert stderr == ''
        assert stdout == 'qux\n'

        when('--option foo.bar.baz=\'quux\' bar')
        assert status == 0
        assert stderr == ''
        assert stdout == 'quux\n'

        when('--option foo bar')
        assert status == 1
        assert stderr == 'Invalid option: -O/--option foo\n'
        assert stdout.startswith('usage: ')


if __name__ == '__main__':
    app.climain()
