import logging
from contextlib import contextmanager


LOG = logging.getLogger('syncano-sync')
SYNCANO_LOG = logging.getLogger('syncano')


@contextmanager
def mute_log(logger=None):
    logger = logger or SYNCANO_LOG
    level = logger.getEffectiveLevel()
    logger.setLevel(logging.ERROR)
    yield
    logger.setLevel(level)
