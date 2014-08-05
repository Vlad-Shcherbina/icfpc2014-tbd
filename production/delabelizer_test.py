import sys

import nose
from nose.tools import eq_

from delabelizer import delabelize


def test_simple():
    input = """
    ; line consisting entirely of comment
    hello 1, 2  ; comment
label:
    world
    goto label
"""
    golden = """
    ; line consisting entirely of comment
    hello 1, 2  ; comment
;label:
    world
    goto 1                                ; --> label
"""
    result = ''.join(line + '\n' for line in delabelize(input.splitlines()))
    print result
    eq_(result, golden)


if __name__ == '__main__':
    nose.run_exit(argv=[
        sys.argv[0], __file__,
        '--verbose', '--with-doctest', '--logging-level=DEBUG'
    ])
