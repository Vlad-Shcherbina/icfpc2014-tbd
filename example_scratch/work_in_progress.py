import sys
sys.path.append('../production')

import logging
logger = logging.getLogger(__name__)


import some_module


def g():
    return some_module.f()**2


if __name__ == '__main__':
    # log from this script at debug,
    # from `some_module` at info,
    # and from everywhere else at warning
    logging.basicConfig(level=logging.WARNING)
    logger.setLevel(logging.DEBUG)
    logging.getLogger('some_module').setLevel(logging.INFO)

    logger.debug('zzz')
    print g()
