import sys

import nose
from nose.tools import eq_

import fj_gcc
import yole_gcc
import vorber_gcc
from asm_parser import parse_gcc

sys.path.append('../vlad_scratch')
import vlad_gcc


def fj_call(code, args):
    machine = fj_gcc.FjGCC(parse_gcc(code))
    return machine.call(0, args)

def yole_call(code, args):
    machine = yole_gcc.GccMachine(parse_gcc(code))
    return machine.call(0, args)

def vorber_call(code, args):
    machine = vorber_gcc.VorberGCC(parse_gcc(code))
    return machine.call(0, args)

def vlad_call(code, args):
    machine = vlad_gcc.VladGCC(parse_gcc(code))
    return machine.call(0, args)

# TODO: fix VorberGCC and enable tests for it as well.
CALLS = [fj_call, yole_call, vlad_call]#, vorber_call]


def test_arithmetic():
    def f(call):
        code = """
        LDC 40
        LDC 10
        SUB
        LDC 2
        MUL
        LDC 7
        DIV
        LDC 34
        ADD
        RTN
        """
        eq_(call(code, []), 42)
    for call in CALLS:
        yield f, call


def test_comparisons():
    def f(call):
        code = """
        LDC 1
        LDC 2
        CEQ
        LDC 2
        LDC 2
        CEQ
        CONS

        LDC 2
        LDC 2
        CGT
        LDC 2
        LDC 1
        CGT
        CONS

        LDC 1
        LDC 2
        CGTE
        LDC 2
        LDC 2
        CGTE
        CONS

        LDC 2
        LDC 2
        CONS
        ATOM
        LDC 1
        ATOM
        CONS

        CONS
        CONS
        CONS

        RTN
        """
        eq_(call(code, []), ((0, 1), ((0, 1), ((0, 1), (0, 1)))))
    for call in CALLS:
        yield f, call


def test_list_ops():
    def f(call):
        code = """
        LDC 41
        LDC 999
        CONS
        CAR
        LDC 999
        LDC 1
        CONS
        CDR
        ADD
        RTN
        """
        eq_(call(code, []), 42)
    for call in CALLS:
        yield f, call


def test_local():
    def f(call):
        code = """
        LDC 21
        LDF 4
        AP 1
        RTN
        LD 0 0
        LD 0 0
        ADD
        RTN
        """
        eq_(call(code, []), 42)
    for call in CALLS:
        yield f, call


def test_tap():
    def f(call):
        code = """
        LDC 21
        LDF 3
        TAP 1
        LD 0 0
        LD 0 0
        ADD
        RTN
        """
        eq_(call(code, []), 42)
    for call in CALLS:
        yield f, call


def test_trap():
    def f(call):
        code = """
        DUM 1
        LDC 21
        LDF 4
        TRAP 1
        LD 0 0
        LD 0 0
        ADD
        RTN
        """
        eq_(call(code, []), 42)
    for call in CALLS:
        yield f, call


def test_sel():
    def f(call):
        code = """
        ldc 0
        sel 3 5
        rtn
        ldc 2
        join
        ldc 42
        join
        """
        eq_(call(code, []), 42)
    for call in CALLS:
        yield f, call


def test_sel_false():
    def f(call):
        code = """
        ldc 2
        sel 3 5
        rtn
        ldc 42
        join
        ldc 1
        join
        """
        eq_(call(code, []), 42)
    for call in CALLS:
        yield f, call


def test_tsel():
    def f(call):
        code = """
        ldc 0
        tsel 2 4
        ldc 2
        rtn
        ldc 42
        rtn
        """
        eq_(call(code, []), 42)
    for call in CALLS:
        yield f, call


if __name__ == '__main__':
    nose.run_exit(argv=[
        sys.argv[0], __file__,
        '--verbose', '--with-doctest', '--logging-level=DEBUG'
    ])
