from bddcli import Application as CLIApplication, Given, stderr, stdout, status

from yhttp.core import __version__


def test_yhttp_version_cli():
    cliapp = CLIApplication('yhttp', 'yhttp.core.main:app.climain')

    with Given(cliapp, '--version'):
        assert status == 0
        assert stdout.strip() == __version__
        assert stderr == ''
