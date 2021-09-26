from bddrest import status, given, when

from yhttp import validate, statuses


def test_nobody(app, Given):

    @app.route()
    @validate(nobody=True)
    def foo(req):
        assert req.form == {}

    with Given(verb='foo'):
        assert status == 200

        when(form=dict(bar='baz'))
        assert status == '400 Body Not Allowed'


def test_required(app, Given):

    @app.route()
    @validate(fields=dict(
        bar=dict(required=True),
        baz=dict(required='700 Please provide baz'),
    ))
    def post(req):
        pass

    with Given(verb='post', form=dict(bar='bar', baz='baz')):
        assert status == 200

        when(form=given - 'bar')
        assert status == '400 Field bar is required'

        when(form=given - 'baz', query=dict(baz='baz'))
        assert status == 200

        when(form=given - 'baz')
        assert status == '700 Please provide baz'


def test_notnone(app, Given):
    @app.route()
    @validate(fields=dict(
        bar=dict(notnone=True),
        baz=dict(notnone='700 baz cannot be null')
    ))
    def post(req):
        pass

    with Given(verb='post', json=dict(bar='bar', baz='baz')):
        assert status == 200

        when(json=given - 'bar')
        assert status == 200

        when(json=given | dict(bar=None))
        assert status == '400 Field bar cannot be null'

        when(json=given - 'baz')
        assert status == 200

        when(json=given | dict(baz=None))
        assert status == '700 baz cannot be null'


def test_readonly(app, Given):

    @app.route()
    @validate(fields=dict(
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
    @validate(fields=dict(
        bar=dict(type_=int),
    ))
    def post(req):
        if 'bar' in req.form:
            assert isinstance(req.form['bar'], int)

    with Given(verb='post'):
        assert status == 200

        when(json=dict(bar='bar'))
        assert status == '400 Invalid type: bar'

        when(json=dict(bar='2'))
        assert status == 200


def test_type_querystring(app, Given):
    @app.route()
    @validate(fields=dict(
        bar=dict(type_=int),
    ))
    def get(req, *, bar=None):
        assert isinstance(req.query['bar'], int)
        assert isinstance(bar, int)

    with Given(query=dict(bar='2')):
        assert status == 200


def test_minimummaximum(app, Given):
    @app.route()
    @validate(fields=dict(
        bar=dict(
            minimum=2,
            maximum=9
        ),
    ))
    def post(req):
        pass

    with Given(verb='post', json=dict(bar=2)):
        assert status == 200

        when(json=dict(bar='bar'))
        assert status == '400 Minimum allowed value for field bar is 2'

        when(json=dict(bar=1))
        assert status == '400 Minimum allowed value for field bar is 2'

        when(json=dict(bar=10))
        assert status == '400 Maximum allowed value for field bar is 9'


def test_minmaxlength(app, Given):
    @app.route()
    @validate(fields=dict(
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


def test_regexpattern(app, Given):
    @app.route()
    @validate(fields=dict(
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
    from yhttp.validation import Field

    def customvalidator(value, container, field):
        assert isinstance(field, Field)
        if value not in 'ab':
            raise statuses.status(400, 'Value must be either a or b')

    @app.route()
    @validate(fields=dict(
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
    @validate(fields=dict(
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
