import nose, sys
from nose.tools import eq_, assert_raises
from fj_gcc import FjGCC as GccMachine, InterpreterException as GccException
from asm_parser import parse_gcc

def test_parser():
    machine = GccMachine(parse_gcc("ldc 3\n ldc 4\n add\n stop"))
    machine.run()
    eq_(machine.data_stack, [7])

def test_local_gcc():
    machine = GccMachine(parse_gcc("""
    LDC 21
    LDF 4
    AP 1
    RTN
    LD 0 0
    LD 0 0
    ADD
    STOP"""))
    machine.run()
    eq_(machine.data_stack, [42])

def test_tap():
    machine = GccMachine(parse_gcc("""
    LDC 21
    LDF 3
    TAP 1
    LD 0 0
    LD 0 0
    ADD
    STOP"""))
    machine.run()
    eq_(machine.data_stack, [42])

def test_trap():
    machine = GccMachine(parse_gcc("""
    DUM 1
    LDC 21
    LDF 4
    TRAP 1
    LD 0 0
    LD 0 0
    ADD
    STOP"""))
    machine.run()
    eq_(machine.data_stack, [42])

def test_sel():
    machine = GccMachine(parse_gcc("""
ldc 0
sel 3 5
stop
ldc 2
join
ldc 42
join
rtn
"""))
    machine.run()
    eq_(machine.data_stack, [42])

def test_sel_false():
    machine = GccMachine(parse_gcc("""
ldc 2
sel 3 5
stop
ldc 42
join
ldc 1
join
rtn
"""))
    machine.run()
    eq_(machine.data_stack, [42])

def test_tsel():
    machine = GccMachine(parse_gcc("""
ldc 0
tsel 2 4
ldc 2
rtn
ldc 42
STOP
"""))
    machine.run()
    eq_(machine.data_stack, [42])

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