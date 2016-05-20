import logging
from contextlib import contextmanager


LOG = logging.getLogger('syncano-cli')
SYNCANO_LOG = logging.getLogger('syncano')

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
LOG.addHandler(handler)
LOG.setLevel(logging.INFO)


@contextmanager
def mute_log(logger=None):  # TODO: probably remove this;
    logger = logger or SYNCANO_LOG
    level = logger.getEffectiveLevel()
    logger.setLevel(logging.INFO)
    yield
    logger.setLevel(level)
