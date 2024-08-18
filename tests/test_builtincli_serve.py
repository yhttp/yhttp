import time

import requests
import pytest
from bddcli import Application as CLIApplication, Given

from yhttp.core import Application, text
from .conftest import GITHUBACTIONS


app = Application()


@app.route('/')
@text
def get(req):
    return 'foo'


@pytest.mark.skipif(
    GITHUBACTIONS,
    reason='no way of currently testing this by GH, due the Github actions bug'
)
def test_servercli(freetcpport):
    cliapp = CLIApplication('foo', 'tests.test_builtincli_serve:app.climain')

    with Given(cliapp, f'serve --bind {freetcpport}', nowait=True) as s:
        url = f'http://localhost:{freetcpport}'
        time.sleep(2)
        r = requests.get(url)
        assert r.text == 'foo'
        s.kill()


if __name__ == '__main__':
    app.climain(['serve'])
