# YHTTP

[![PyPI](https://img.shields.io/pypi/v/yhttp.svg)](https://pypi.org/project/yhttp/)
[![Build](https://github.com/yhttp/yhttp/actions/workflows/build.yml/badge.svg)](https://github.com/yhttp/yhttp/actions/workflows/build.yml)
[![Coverage](https://coveralls.io/repos/github/yhttp/yhttp/badge.svg?branch=master)](https://coveralls.io/github/yhttp/yhttp?branch=master)
[![Documentation](https://img.shields.io/badge/docs-yhttp.github.io-blue)](https://yhttp.github.io/yhttp/)
[![Python](https://img.shields.io/badge/Python-%3E%3D3.10-blue)](https://www.python.org/)

YHTTP is a small, extensible WSGI framework for building HTTP services in
Python. It provides regex routing, request guards, form parsing, settings,
lifecycle hooks, static file serving, and a built-in development CLI while
leaving features such as templates, authentication, localization, and database
access to focused extensions.

- [Documentation](https://yhttp.github.io/yhttp/)
- [PyPI](https://pypi.org/project/yhttp/)
- [Source](https://github.com/yhttp/yhttp)

## Installation

YHTTP requires Python 3.10 or newer.

```bash
python -m pip install yhttp
```

## Quick start

Create `hello.py`:

```python
import sys

from yhttp.core import Application, text


app = Application('0.1.0', 'hello')


@app.route('/')
@text
def get(req):
    return 'Hello, world!'


if __name__ == '__main__':
    sys.exit(app.climain())


app.ready()
```

Start the built-in development server and make a request:

```bash
python hello.py serve --bind 8080
curl http://localhost:8080/
```

The application is WSGI-compatible, so it can also be served by a WSGI server
such as Gunicorn:

```bash
python -m pip install gunicorn
gunicorn hello:app
```

The handler name selects the HTTP verb when `verb` is not passed explicitly to
`app.route()`. Routes are regular expressions, and captured groups are passed
to the handler after `req`.

## Features

- Regex routes with captured path parameters and explicit verb overrides
- Strict query-string and request-body validation through guards
- URL-encoded, multipart, and JSON form parsing
- Layered settings and application lifecycle hooks
- Static files, WSGI rewriting, middleware, and status handlers
- An extensible command-line interface with a development server
- A small core that can be composed with YHTTP extensions

## SSR development

YHTTP keeps server-side rendering outside the core. Use an extension such as
[`yhttp-mako`](https://github.com/yhttp/yhttp-mako) to render Mako templates,
then compose localization, authentication, assets, and persistence through the
extensions already used by your application.

Install the Mako extension:

```bash
python -m pip install yhttp-mako
mkdir -p templates makomodules
```

A minimal rendered page consists of an application module and a template:

```python
# app.py
from yhttp.core import Application
from yhttp.ext import mako


app = Application('0.1.0', 'pages')
mako.install(app)

app.settings.mako.lookup = 'templates'
app.settings.mako.modules = 'makomodules'


@app.route('/')
@app.template('index.mako')
def get(req):
    return {'title': 'Hello from YHTTP'}


app.ready()
```

```mako
<!-- templates/index.mako -->
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>${title | h}</title>
  </head>
  <body>
    <h1>${title | h}</h1>
  </body>
</html>
```

Run it with `gunicorn app:app`. The `makomodules` directory stores compiled
templates and must be writable by the application process.

For a maintainable SSR application, keep the rendering path explicit:

1. Create the `Application`, install extensions, and merge settings before
   readiness. Import model modules before route modules, and call `app.ready()`
   only after registration is complete; an unimported model or route module is
   inactive.
2. Keep handlers responsible for request guards, authorization, database
   access, and status responses. A page handler should return a context
   dictionary to `@app.template(...)`, not build HTML itself.
3. Put shared document structure in inherited Mako layouts. Keep templates
   presentational, reuse template-provided helpers, and escape user-controlled
   values. Render stored HTML unescaped only when the application explicitly
   treats it as trusted.
4. Localize visible text with the installed translation helpers, preserve
   locale-prefixed links, and test both LTR and RTL output when the application
   supports both directions.
5. Keep pages useful without JavaScript where practical. Add focused browser
   behavior through the project's existing asset pipeline, and keep endpoint
   calls in browser-side service modules rather than templates.
6. Extend the nearest bddrest page test. Assert meaningful rendered behavior,
   including routes, localized text, direction-sensitive markup, resolved
   assets, authentication states, and persisted effects relevant to the page.

A typical project keeps its composition root, route registration, page
handlers, templates, browser assets, and page tests separate:

```text
app.py
models/
routes.py
pages.py
templates/
www/
tests/test_pages.py
```

Treat this as a responsibility map rather than a required package layout;
follow the nearest complete feature in an existing application.

## Contributing

This repository uses
[`python-makelib`](https://github.com/pylover/python-makelib). Install it first,
then create and populate the development environment:

```bash
make venv
source ./activate.sh
make env
```

Run the test suite:

```bash
make test
```

Run a focused test or coverage target with `F`:

```bash
make test F=tests/test_form.py::test_getform_force
make cover F=tests/test_static.py
```

Run all coverage checks or generate the HTML coverage report:

```bash
make cover
make cover-html
```

Lint the project:

```bash
make lint
```

Delete the virtual environment with `make venv-delete`.

## Documentation

Build and test the Sphinx documentation from the repository root:

```bash
source ./activate.sh
make doc
make doctest
make doclive
```

The equivalent commands from `sphinx/` are `make html`, `make doctest`, and
`make livehtml`.

## Distribution

Build the source and wheel distributions in `dist/`:

```bash
make clean
make sdist
make wheel
```

Publishing is reserved for project maintainers. Maintainers can upload both
artifacts with `make pypi`.

## License

YHTTP is released under the [MIT License](LICENSE).
