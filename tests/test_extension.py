from bddrest import status


def fooextension(app):
    @app.when
    def ready(app):
        app.fooready = True


def test_extension(app, story, when):
    fooextension(app)

    app.ready()
    assert app.fooready

