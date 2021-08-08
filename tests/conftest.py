import os
import shutil
import socket
import tempfile
import functools

import bddrest
import pytest

from yhttp import Application


@pytest.fixture
def app():
    return Application()


@pytest.fixture
def Given(app):
    return functools.partial(bddrest.Given, app)


@pytest.fixture
def freetcpport():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((socket.gethostname(), 0))
        return s.getsockname()[1]
    finally:
        s.close()


@pytest.fixture
def tempstruct():
    temp_directories = []

    def create_nodes(root, **kw):
        for k, v in kw.items():
            name = os.path.join(root, k)

            if isinstance(v, dict):
                os.mkdir(name)
                create_nodes(name, **v)
                continue

            if hasattr(v, 'read'):
                f = v
                v = f.read()
                f.close()

            with open(name, 'w') as f:
                f.write(v)

    def _make_temp_directory(**kw):
        """Structure example: {'a.html': 'Hello', 'b': {}}."""
        root = tempfile.mkdtemp()
        temp_directories.append(root)
        create_nodes(root, **kw)
        return root

    yield _make_temp_directory

    for d in temp_directories:
        shutil.rmtree(d)
