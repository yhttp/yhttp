#! /usr/bin/env python3
import time
from wsgiref.simple_server import make_server

from yhttp import Application, text


app = Application()


@app.route()
@text
def get(res, resp):
    i = 0
    while True:
        yield f'{i:04}\r\n'.encode()
        time.sleep(1)
        i += 1


#@app.route()
#@text
#def get():
#    return 'index'



if __name__ == '__main__':
    httpd = make_server('', 8000, app)
    print('Demo server started http://localhost:8000')
    httpd.serve_forever()
