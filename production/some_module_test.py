from nose.tools import eq_

import some_module


def test1():
    assert True
    eq_(some_module.f(), 42)
