from bddcli import Application as CLIApplication, Given, stderr, stdout, \
    status, when

from yhttp.core import Application, __version__


app = Application(__version__, 'foo')


def test_versioncli():
    cliapp = CLIApplication('foo', 'tests.test_builtincli_version:app.climain')

    with Given(cliapp, '--version'):
        assert status == 0
        assert stdout.strip() == __version__
        assert stderr == ''

        when('')
        assert status == 0
        assert stderr == ''


if __name__ == '__main__':
    app.climain(['--version'])
