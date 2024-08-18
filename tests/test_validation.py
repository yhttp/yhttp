import pytest
from bddrest import status, given, when

from yhttp.core import validate_form, validate_query, statuses
from yhttp.core.validation import TypeValidator, Field


def test_nobody(app, Given):

    @app.route()
    @validate_form(nobody=True)
    def foo(req):
        assert req.getform(relax=True) is None

    with Given(verb='foo'):
        assert status == 200

        when(form=dict(bar='baz'))
        assert status == '400 Body Not Allowed'

        when(query=dict(bar='baz'))
        assert status == 200


def test_nobody_get(app, Given):

    @app.route()
    @validate_form(nobody=True)
    def get(req, *, bar=None):
        assert req.query.get('bar') == bar
        assert req.getform(relax=True) is None

    with Given():
        assert status == 200

        when(query=dict(bar='baz'))
        assert status == 200


def test_required(app, Given):

    @app.route()
    @validate_query(fields=dict(
        foo=dict(required=True),
    ))
    @validate_form(fields=dict(
        bar=dict(required=True),
        baz=dict(required=statuses.forbidden()),
    ))
    def post(req):
        pass

    with Given(verb='post', query=dict(foo='foo'),
               form=dict(bar='bar', baz='baz')):
        assert status == 200

        when(form=given - 'bar')
        assert status == '400 Field bar is required'

        when(form=given - 'baz', query=given + dict(baz='baz'))
        assert status == '403 Forbidden'

        when(form=given - 'baz')
        assert status == '403 Forbidden'


def test_readonly(app, Given):

    @app.route()
    @validate_form(fields=dict(
        bar=dict(readonly=True),
    ))
    def post(req):
        pass

    with Given(verb='post'):
        assert status == 200

        when(form=dict(bar='bar'))
        assert status == '400 Field bar is readonly'


def test_type(app, Given):
    @app.route()
    @validate_form(fields=dict(
        bar=dict(type_=int),
    ))
    def post(req):
        form = req.getform(relax=True)
        if form and 'bar' in form:
            assert isinstance(form['bar'], int)

    with Given(verb='post'):
        assert status == 200

        when(form=dict(bar='bar'))
        assert status == '400 Invalid type: `str` for field `bar`'

        when(form=dict(bar='2'))
        assert status == 200


def test_ontypeerror(app, Given):
    with pytest.raises(ValueError):
        TypeValidator('str', onerror='bar')

    @app.route()
    @validate_form(fields=dict(
        foo=dict(type_=str, ontypeerror='raise'),
        bar=dict(type_=int, ontypeerror='raise'),
    ))
    def post(req):
        form = req.getform(relax=True)
        if form and 'bar' in form:
            assert isinstance(form['bar'], int)

    with Given(verb='post'):
        assert status == 200

        when(form=dict(foo='foo'))
        assert status == 200

        when(form=dict(bar='bar'))
        assert status == '400 Invalid type: bar'

        when(form=dict(bar='2'))
        assert status == '400 Invalid type: bar'


def test_type_querystring(app, Given):
    @app.route()
    @validate_query(fields=dict(
        bar=dict(
            type_=int
        ),
    ))
    def get(req, *, bar=None):
        assert isinstance(req.query['bar'], int)
        assert isinstance(bar, int)

    with Given(query=dict(bar='2')):
        assert status == 200


def test_minimummaximum(app, Given):
    @app.route()
    @validate_form(fields=dict(
        bar=dict(
            type_=int,
            minimum=2,
            maximum=9
        ),
    ))
    def post(req):
        pass

    with Given(verb='post', form=dict(bar='2')):
        assert status == 200

        when(form=dict(bar='bar'))
        assert status == '400 Invalid type: `str` for field `bar`'

        when(form=dict(bar='1'))
        assert status == '400 Minimum allowed value for field bar is 2'

        when(form=dict(bar='10'))
        assert status == '400 Maximum allowed value for field bar is 9'


def test_minmaxlength(app, Given):
    @app.route()
    @validate_form(fields=dict(
        bar=dict(minlength=2, maxlength=5),
    ))
    def post(req):
        pass

    with Given(verb='post', form=dict(bar='123')):
        assert status == 200

        when(form=given - 'bar')
        assert status == 200

        when(form=given | dict(bar='1'))
        assert status == '400 Minimum allowed length for field bar is 2'

        when(form=given | dict(bar='123456'))
        assert status == '400 Maximum allowed length for field bar is 5'


def test_length(app, Given):
    @app.route()
    @validate_form(fields=dict(
        bar=dict(length=6),
    ))
    def post(req):
        pass

    with Given(verb='post', form=dict(bar='123456')):
        assert status == 200

        when(form=given - 'bar')
        assert status == 200

        when(form=dict(bar='12345'))
        assert status == '400 Allowed length for field bar is 6'

        when(form=dict(bar='12345678'))
        assert status == '400 Allowed length for field bar is 6'


def test_regexpattern(app, Given):
    @app.route()
    @validate_form(fields=dict(
        bar=dict(pattern=r'^\d+$'),
        baz=dict(pattern=(r'\d+$', '400 Only Integer'))
    ))
    def post(req):
        pass

    with Given(verb='post', form=dict(bar='123')):
        assert status == 200

        when(form=given - 'bar')
        assert status == 200

        when(form=given | dict(bar='a'))
        assert status == '400 Invalid format: bar'

        when(form=given + dict(baz='alphabet'))
        assert status == '400 Only Integer'


def test_customvalildator(app, Given):
    def customvalidator(req, value, container, field):
        assert isinstance(field, Field)
        for v in value:
            if v not in 'ab':
                raise statuses.status(400, 'Value must be either a or b')

    @app.route()
    @validate_form(fields=dict(
        bar=dict(callback=customvalidator)
    ))
    def post(req):
        pass

    with Given(verb='post', form=dict(bar='a')):
        assert status == 200

        when(form=given - 'bar')
        assert status == 200

        when(form=given | dict(bar='c'))
        assert status == '400 Value must be either a or b'

    @app.route()
    @validate_form(fields=dict(
        bar=customvalidator
    ))
    def post(req):  # noqa: W0404
        pass

    with Given(verb='post', form=dict(bar='a')):
        assert status == 200

        when(form=given - 'bar')
        assert status == 200

        when(form=given | dict(bar='c'))
        assert status == '400 Value must be either a or b'


def test_extraattribute(app, Given):

    @app.route()
    @validate_form(strict=True)
    def post(req):
        pass

    @app.route()
    @validate_form()
    def put(req):
        pass

    with Given(verb='post', form=dict(bar='123')):
        assert status == 400

        when(verb='put')
        assert status == 200

        when(verb='put', form=given - 'bar')
        assert status == 200

        when(form=given - 'bar')
        assert status == 411
