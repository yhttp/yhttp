import os
import shutil
import tempfile
import functools

import bddrest
import pytest

from yhttp.core import Application
from yhttp.dev.fixtures import mockupfs, freetcpport


GITHUBACTIONS = 'CI' in os.environ and os.environ['CI'] \
    and 'GITHUB_RUN_ID' in os.environ


@pytest.fixture
def app():
    return Application()


@pytest.fixture
def Given(app):
    return functools.partial(bddrest.Given, app)
