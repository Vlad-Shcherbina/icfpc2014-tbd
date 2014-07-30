import sys
import nose
from nose.tools import eq_, raises

from goto import goto, MissingLabelError, DuplicateLabelError


@goto
def test_simple():
    visited = []
    visited.append(1)
    goto .next
    visited.append(2)
    label .next
    visited.append(3)
    eq_(visited, [1, 3])


@goto
def test_loop():
    visited = []
    i = 0
    visited.append(42)
    label .loop
    i += 1
    visited.append(i)
    if i < 3:
        goto .loop
    visited.append(43)
    eq_(visited, [42, 1, 2, 3, 43])


@raises(MissingLabelError)
def test_missing_label():
    @goto
    def f():
        goto .missing_label


@raises(DuplicateLabelError)
def test_duplicate_label():
    @goto
    def f():
        label .x
        label .x


@goto
def test_go_to_label_twice():
    """
    Exposes defect in the original recipe from
    http://code.activestate.com/recipes/576944/
    """
    i = 0
    visited = []
    visited.append(1)
    goto .next
    visited.append(2)
    label .next
    visited.append(3)
    if i == 0:
        i = 1
        goto .next
    visited.append(4)
    eq_(visited, [1, 3, 3, 4])


if __name__ == '__main__':
    nose.run_exit(argv=[
        sys.argv[0], __file__,
        '--verbose', '--with-doctest', '--logging-level=DEBUG'
    ])
