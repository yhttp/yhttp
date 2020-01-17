# yhttp



[![PyPI](http://img.shields.io/pypi/v/yhttp.svg)](https://pypi.python.org/pypi/yhttp)
[![Build Status](https://travis-ci.org/yhttp/yhttp.svg?branch=master)](https://travis-ci.org/yhttp/yhttp)
[![Coverage Status](https://coveralls.io/repos/github/yhttp/yhttp/badge.svg?branch=master)](https://coveralls.io/github/yhttp/yhttp?branch=master)


## Contribution


### Quickstart

wsgi.py


```python

app = Applicatin()

@app.route('/')
def get(req):
    return 'Hello world!'

```


```bash
gunicorn wsgi:app
```

