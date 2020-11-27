def fooextension(app):
    @app.when
    def ready(app):
        app.fooready = True

    @app.when
    def shutdown(app):
        app.fooshutdown = True


def test_extension(app):
    fooextension(app)

    app.ready()
    assert app.fooready

    app.shutdown()
    assert app.fooshutdown
