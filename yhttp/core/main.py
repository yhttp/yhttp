from .version import __version__
from . import Application


app = Application(__version__, 'yhttp')
app.settings.debug = False
app.staticdirectory('/', '.', default=True)
app.ready()
