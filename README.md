# rehttp



[![PyPI](http://img.shields.io/pypi/v/rehttp.svg)](https://pypi.python.org/pypi/rehttp)
[![Build Status](https://travis-ci.org/pylover/rehttp.svg?branch=master)](https://travis-ci.org/pylover/rehttp)
[![Coverage Status](https://coveralls.io/repos/github/pylover/rehttp/badge.svg?branch=master)](https://coveralls.io/github/pylover/rehttp?branch=master)


## Contribution


### Quickstart

wsgi.py


```python

app = Applicatin()

@app.route('/foos')
def get():
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

