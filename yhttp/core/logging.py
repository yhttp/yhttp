import sys

from logging import basicConfig, WARNING, ERROR, CRITICAL, INFO, DEBUG, \
    getLogger as getlogger, getLevelNamesMapping as getlevelnamesmapping


_configured = False
logger = getlogger('yhttp')


def configure(verbosity):
    global _configured

    if _configured:
        logger.info('Logging already configured')
        return

    basicConfig(
        level=verbosity,
        stream=sys.stdout,
        format="{asctime}.{msecs:03.0f} {levelname} {name}: {message}",
        style="{",
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    _configured = True
