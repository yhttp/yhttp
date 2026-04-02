import time

import requests
from bddcli import Application as CLIApplication, Given

from yhttp.core import Application, text


app = Application('0.1.0', 'foo')


@app.route('/')
@text
def get(req):
    return 'foo'


def test_servercli(freetcpport):
    cliapp = CLIApplication('foo', 'tests.test_builtincli_serve:app.climain')

    with Given(cliapp, f'serve --bind {freetcpport}', nowait=True) as s:
        url = f'http://localhost:{freetcpport}'
        time.sleep(5)
        r = requests.get(url)
        assert r.text == 'foo'
        s.kill()
