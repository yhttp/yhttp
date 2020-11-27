#! /usr/bin/env python3
import time
from wsgiref.simple_server import make_server

from yhttp import Application, text, json


app = Application()


app.staticfile('/demo', 'demo/demo.py')


@app.route('/json')
@json
def get(req):  # noqa: W0404
    return {'foo': 'bar'}


@app.route('/json')
@json
def post(req):  # noqa: W0404
    return req.form


@app.route(r'/(.*)')
@text
def get(req, resource):  # noqa: W0404
    i = 0
    while True:
        yield f'{req.path} {i:04}\r\n'.encode()
        time.sleep(1)
        i += 1


if __name__ == '__main__':
    httpd = make_server('', 8000, app)
    print('Demo server started http://localhost:8000')
    httpd.serve_forever()
