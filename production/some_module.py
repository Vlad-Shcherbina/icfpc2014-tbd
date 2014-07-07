import logging
logger = logging.getLogger(__name__)


def f():
    '''
    Helpful usage example (which is also a test):
    >>> f()
    42
    '''
    logger.info('f...')
    return 42
