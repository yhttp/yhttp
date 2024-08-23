# yhttp

[![PyPI](http://img.shields.io/pypi/v/yhttp.svg)](https://pypi.python.org/pypi/yhttp)
[![Build](https://github.com/yhttp/yhttp/actions/workflows/build.yml/badge.svg)](https://github.com/yhttp/yhttp/actions/workflows/build.yml)
[![Coverage Status](https://coveralls.io/repos/github/yhttp/yhttp/badge.svg?branch=master)](https://coveralls.io/github/yhttp/yhttp?branch=master)
[![Documentation](https://img.shields.io/badge/Documentation-almost%20done!-blue)](https://yhttp.github.io/yhttp)
[![Python](https://img.shields.io/badge/Python-%3E%3D3.10-blue)](https://python.org)

[Documentation](https://yhttp.github.io/yhttp)

## Contribution

### python-makelib
Install [python-makelib](https://github.com/pylover/python-makelib).

### Clone 
```bash
git clone --recurse-submodules git@github.com:yhttp/yhttp.git
```

### Virtualenv

Create virtual environment:
```bash
make venv
```

Delete virtual environment:
```bash
make venv-delete
```

Activate the virtual environment:
```bash
source ./activate.sh
```


### Install (editable mode)
Install this project as editable mode and all other development dependencies:
```bash
make env
```


### Tests
Execute all tests:
```bash
make test
```

Execute specific test(s) using wildcard:
```bash
make test F=tests/test_db*
make test F=tests/test_form.py::test_querystringform
```

*refer to* [pytest documentation](https://docs.pytest.org/en/7.1.x/how-to/usage.html#how-to-invoke-pytest)
*for more info about invoking tests.*

Execute tests and report coverage result:
```bash
make cover
make cover F=tests/test_static.py
make cover-html
```


# Lint
```bash
make lint
```


### Distribution
Execute these commands to create `Python`'s standard distribution packages
at `dist` directory:
```bash
make sdist
make wheel
```

Or 
```bash
make dist
```
to create both `sdidst` and `wheel` packages.


### Clean build directory
Execute: 
```bash
make clean
```
to clean-up previous `dist/*` and `build/*` directories.


### PyPI

> **_WARNING:_** Do not do this if you'r not responsible as author and 
> or maintainer of this project.

Execute
```bash
make clean
make pypi
```
to upload `sdists` and `wheel` packages on [PyPI](https://pypi.org).


## Documentation

```bash
make doc
make livedoc
make doctest
```

Or 

```bash
cd sphinx
make doctest
make html
make livehtml
```
