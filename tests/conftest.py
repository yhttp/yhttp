import os
import shutil
import tempfile
import functools

from bddcli.fixtures import bootstrapper_patch
import bddrest
import pytest

from yhttp.core import Application


@pytest.fixture
def app():
    return Application('0.1.0', 'foo')


@pytest.fixture
def httpreq(app):
    return functools.partial(bddrest.Given, app)


@pytest.fixture
def bddcli_bootpatch():
    return bootstrapper_patch
