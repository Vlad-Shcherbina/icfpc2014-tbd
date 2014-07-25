import sys
sys.path.append('../production')

import logging
log = logging.getLogger(__name__)


import some_module


def g():
    return some_module.f()**2


def main():
    # log from this script at debug,
    # from `some_module` at info,
    # and from everywhere else at warning
    logging.basicConfig(level=logging.WARNING)
    log.setLevel(logging.DEBUG)
    logging.getLogger('some_module').setLevel(logging.INFO)

    log.debug('zzz')
    print g()


if __name__ == '__main__':
    main()
