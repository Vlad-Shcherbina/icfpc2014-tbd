import sys
sys.path.append('../production')

import logging
log = logging.getLogger(__name__)
from pprint import pprint

import dis

def to_int32(x):
    return (x & 0xFFFFFFFF) - ((x & 0x80000000) << 1)

def do_stuff():
    for x in xrange(-20, 20):
        print to_int32(2**32 + x)
    

def main():
    # log from this script at debug,
    # from `some_module` at info,
    # and from everywhere else at warning
    logging.basicConfig(level=logging.WARNING)
    log.setLevel(logging.DEBUG)
    logging.getLogger('some_module').setLevel(logging.INFO)
    log.debug('start')
    do_stuff()
    log.debug('end')



if __name__ == '__main__':
    main()
