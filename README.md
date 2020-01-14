# yhttp



[![PyPI](http://img.shields.io/pypi/v/yhttp.svg)](https://pypi.python.org/pypi/yhttp)
[![Build Status](https://travis-ci.org/yhttp/yhttp.svg?branch=master)](https://travis-ci.org/yhttp/yhttp)
[![Coverage Status](https://coveralls.io/repos/github/yhttp/yhttp/badge.svg?branch=master)](https://coveralls.io/github/yhttp/yhttp?branch=master)


## Contribution


### Quickstart

wsgi.py


```python

app = Applicatin()

@app.route('/foos')
def get(req, resp):
    return 'Hello world!'

```


```bash
gunicorn wsgi:app
```

#### Master branch

The master branch is an integration branch where bug fixes/features are 
gathered for compiling and functional testing. so it would be unstable.

#### Release branch

The release branch is where releases are maintained and hot fixes 
(with names like release/v2.x.x) are added. Please ensure that all your 
production-related work are tracked with the release branches.

With this new model, we can push out bug fixes more quickly and achieve 
simpler maintenance.

