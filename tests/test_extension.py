from bddrest import status


class Foo:
    setupdone = False
    configuredone = False

    def setup(self, app):
        self.setupdone = True

    def configure(self, app):
        self.configuredone = True


def test_extension(app, story, when):
    extension = Foo()
    app.extend(extension)
    assert extension.setupdone

    app.configure_extensions()
    assert extension.configuredone

    @app.route()
    def get(req):
        return 'index'

    with story(app):
        assert status == 200

