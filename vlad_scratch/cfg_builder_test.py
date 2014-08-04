import sys

import nose
from nose.tools import eq_

from cfg_builder import CfgBuilderDemo


def test_demo():
    def f():
        action('begin')
        while nondet():
            action('loop1')
            if nondet():
                break
            action('loop2')
        join()
        action('end')

    builder = CfgBuilderDemo()
    builder.explore(f)

    listing = builder.get_listing()
    print listing

    golden = """
***begin***:
    begin @ f:11
f:12-nondet:
    toss a coin
    False -> f:12-false
f:12-true:
    loop1 @ f:13
f:14-nondet:
    toss a coin
    False -> f:14-false
f:14-true:
    goto -> f:17
f:14-false:
    loop2 @ f:16
    goto -> f:12-nondet
f:12-false:
f:17:
    end @ f:18
***end***:
""".lstrip()
    eq_(listing, golden)


if __name__ == '__main__':
    nose.run_exit(argv=[
        sys.argv[0], __file__,
        '--verbose', '--with-doctest', '--logging-level=DEBUG'
    ])
