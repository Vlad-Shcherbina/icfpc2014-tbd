import sys
sys.path.append('../production')

import logging
log = logging.getLogger(__name__)
from pprint import pprint
from gcc_utils import cons_to_list  

import dis

def to_int32(x):
    return (x & 0xFFFFFFFF) - ((x & 0x80000000) << 1)

def do_stuff():
    code, field = (999888777, (((0, 0), ((0, 0), ((0, 0), ((0, 0), ((0, 0), 0))))), (((0, 0), ((0, 0), ((0, 0), ((0, 0), ((0, 0), 0))))), (((0, 0), ((0, 0), ((0, 0), ((0, 0), ((0, 0), 0))))), (((0, 0), ((0, 0), ((0, 0), ((0, 0), ((0, 0), 0))))), (((0, 0), ((0, 0), ((0, 0), ((0, 0), ((0, 0), 0))))), 0))))))
    pprint([cons_to_list(line) for line in cons_to_list(field)])
    pprint(map(cons_to_list, cons_to_list(field)))

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
