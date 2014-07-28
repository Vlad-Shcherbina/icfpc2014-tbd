import sys
import os
import unittest
import ast
import pprint
import nose
from nose.tools import eq_

from gcc_utils import lto_to_cons, cons_to_list, cons_to_tuple, mat_to_cons, cons_to_mat
from gcc_ast_converter import convert_python_to_gcc_module
from gcc_ast import GccTextBuilder
from asm_parser import parse_gcc
from yole_gcc import GccMachine
from map_loader import load_map
from gcc_wrapper import GCCWrapper


def call(script, func_name, *args):
    text = open(os.path.join("../data/gcpy", script)).read()
    python_ast = ast.parse(text)
    gcc_program = convert_python_to_gcc_module(python_ast)
    builder = GccTextBuilder()
    gcc_program.emit(builder)
    #print builder.text

    addr = builder.labels['$func_{}$'.format(func_name)]
    assert isinstance(addr, int)

    print '** calling {} at {}'.format(func_name, addr)
    print '** with args'
    for arg in args:
        pprint.pprint(arg)

    machine = GccMachine(parse_gcc(builder.text), builder)

    result = machine.call(addr, *args)

    print '** got result'
    pprint.pprint(result)

    return result


def list_length_test():
    for script in 'list_length.py', 'ff.py':
        assert call(script, 'list_length', lto_to_cons([])) == 0
        assert call(script, 'list_length', lto_to_cons(range(5))) == 5


def list_append_test():
    assert (
        cons_to_list(call('ff.py', 'list_append', lto_to_cons([]), 42))
        == [42])

    assert (
        cons_to_list(call('ff.py', 'list_append', lto_to_cons(range(3)), 42))
        == [0, 1, 2, 42])


def list_update_test():
    assert (
        cons_to_list(call('ff.py',
            'list_update', lto_to_cons([42]), 0, 43))
        == [43])
    assert (
        cons_to_list(call('ff.py',
            'list_update', lto_to_cons(range(6)), 3, 42))
        == [0, 1, 2, 42, 4, 5])


def list_at_test():
    assert call('ff.py', 'list_at', lto_to_cons(range(0, 100, 10)), 5) == 50


def link_map_test():
    assert (
        cons_to_list(call('ff.py',
            'list_inc_for_test', lto_to_cons(range(5))))
        == range(1, 6))


def link_map_test():
    result = cons_to_mat(call('ff.py',
            'matrix_inc_for_test', mat_to_cons([[1, 2], [8, 7]])))
    eq_(result, [[2, 3], [9, 8]])


def shift_up_test():
    d = call('ff.py', 'default')
    result = cons_to_mat(call('ff.py',
            'shift_up', mat_to_cons([
                [1, 2],
                [8, 7]])))
    eq_(result, [
        [8, 7],
        [d, d]])



if __name__ == '__main__':
    nose.run_exit(argv=[
        sys.argv[0], __file__,
        '--verbose', '--with-doctest', '--logging-level=DEBUG'
    ])
