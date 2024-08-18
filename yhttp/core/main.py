from . import Application


app = Application()
app.settings.debug = False
app.staticdirectory('/', '.', default=True)
app.ready()
