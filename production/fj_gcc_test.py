import nose, sys
from nose.tools import eq_, assert_raises
from fj_gcc import FjGCC as GccMachine, InterpreterException as GccException
from asm_parser import parse_gcc

def test_parser():
    machine = GccMachine(parse_gcc("ldc 3\n ldc 4\n add\n stop"))
    machine.run()
    eq_(machine.data_stack, [7])

def test_call():
    code = open("../data/lms/miner.gcc").read()
    machine = GccMachine(parse_gcc(code))
    state, step = machine.call(0, 0, 0)
    new_state, direction = machine.call(step, state, 0)
    eq_(2, direction)

def test_max_ticks():
    code = open("../data/lms/miner.gcc").read()
    machine = GccMachine(parse_gcc(code))
    assert_raises(GccException, lambda: machine.call(0, 0, 0, max_ticks=3))


if __name__ == '__main__':
    nose.run_exit(argv=[
        sys.argv[0], __file__,
        '--verbose', '--with-doctest', '--logging-level=DEBUG'
    ])
