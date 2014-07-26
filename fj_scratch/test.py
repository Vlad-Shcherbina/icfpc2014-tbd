import sys
sys.path.append('../production')

import logging
log = logging.getLogger(__name__)

import dis

def f(f_p):
    f_l = 3
    def g(g_p):
        g_l = f_p + f_l
        return g_l + g_p
    return g

def long_ass_function():
    pass


def do_stuff():
    dis.dis(f)
    print
    dis.dis(f(1))
    # long_ass


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
