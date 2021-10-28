import os
import shutil
import tempfile
import functools

import bddrest
import pytest
from yhttp_devutils.fixtures import mockupfs, freetcpport

from yhttp import Application


@pytest.fixture
def app():
    return Application()


@pytest.fixture
def Given(app):
    return functools.partial(bddrest.Given, app)
