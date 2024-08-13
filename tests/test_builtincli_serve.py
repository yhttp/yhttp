import time

import requests
from bddcli import Application as CLIApplication, Given

from yhttp import Application, text


app = Application()


@app.route('/')
@text
def get(req):
    return 'foo'


def test_servercli(freetcpport):
    cliapp = CLIApplication('foo', 'tests.test_builtincli_serve:app.climain')

    from pudb import set_trace; set_trace()
    with Given(cliapp, f'serve --bind {freetcpport}', nowait=True) as s:
        url = f'http://localhost:{freetcpport}'
        time.sleep(1)
        r = requests.get(url)
        assert r.text == 'foo'
        s.kill()


if __name__ == '__main__':
    app.climain(['serve'])
