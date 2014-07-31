import sys

import nose
from nose.tools import eq_

import fj_gcc
import yole_gcc
import vorber_gcc
from asm_parser import parse_gcc


MACHINE_CLASSES = [
    fj_gcc.FjGCC,
    yole_gcc.GccMachine,
    vorber_gcc.VorberGCC,
]


def fj_call(code, args):
    machine = fj_gcc.FjGCC(parse_gcc(code))
    return machine.call(0, args)

def yole_call(code, args):
    machine = yole_gcc.GccMachine(parse_gcc(code))
    return machine.call(0, args)

def vorber_call(code, args):
    machine = vorber_gcc.VorberGCC(parse_gcc(code))
    return machine.call(0, args)

CALLS = [fj_call, yole_call, vorber_call]


def test_add():
    def f(call):
        code = """
        LDC 21
        LDC 21
        ADD
        RTN
        """
        eq_(call(code, []), 42)
    for call in CALLS:
        yield f, call


if __name__ == '__main__':
    nose.run_exit(argv=[
        sys.argv[0], __file__,
        '--verbose', '--with-doctest', '--logging-level=DEBUG'
    ])
