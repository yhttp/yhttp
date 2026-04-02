import os
import shutil
import tempfile
import functools

import bddrest
import pytest

from yhttp.core import Application


@pytest.fixture
def app():
    return Application('0.1.0', 'foo')


@pytest.fixture
def Given(app):
    return functools.partial(bddrest.Given, app)
