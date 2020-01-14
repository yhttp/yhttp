import functools

import bddrest
import pytest

from yhttp import Application


@pytest.fixture
def app():
    return Application()


@pytest.fixture
def story():
    def given_(app, *a, **kw):
        return bddrest.Given(app, None, *a, **kw)

    return given_


@pytest.fixture
def when():
    return functools.partial(bddrest.when, None)


