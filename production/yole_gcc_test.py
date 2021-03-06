from unittest import TestCase
from yole_gcc import GccMachine, GccException
from asm_parser import parse_gcc


class GccTest(TestCase):
    def setUp(self):
        self.gcc_machine = GccMachine()

    def test_ldc(self):
        self.gcc_machine.ldc(3)
        self.assertEquals(self.gcc_machine.data_stack, [3])

    def test_dum(self):
        self.gcc_machine.dum(3)
        self.assertEquals(len(self.gcc_machine.current_frame.values), 3)

    def test_st(self):
        self.gcc_machine.ldc(3)
        self.gcc_machine.dum(1)
        self.gcc_machine.current_frame.dummy = False
        self.gcc_machine.st(0, 0)
        self.assertEquals(3, self.gcc_machine.current_frame.values[0])

    def test_ld(self):
        self.gcc_machine.ldc(3)
        self.gcc_machine.dum(1)
        self.gcc_machine.current_frame.dummy = False
        self.gcc_machine.st(0, 0)
        self.gcc_machine.ld(0, 0)
        self.assertEquals(self.gcc_machine.data_stack, [3])

    def test_add(self):
        self.gcc_machine.ldc(3)
        self.gcc_machine.ldc(4)
        self.gcc_machine.add()
        self.assertEquals(self.gcc_machine.data_stack, [7])

    def test_sub(self):
        self.gcc_machine.ldc(3)
        self.gcc_machine.ldc(4)
        self.gcc_machine.sub()
        self.assertEquals(self.gcc_machine.data_stack, [-1])

    def test_mul(self):
        self.gcc_machine.ldc(3)
        self.gcc_machine.ldc(4)
        self.gcc_machine.mul()
        self.assertEquals(self.gcc_machine.data_stack, [12])

    def test_div(self):
        self.gcc_machine.ldc(14)
        self.gcc_machine.ldc(4)
        self.gcc_machine.div()
        self.assertEquals(self.gcc_machine.data_stack, [3])

    def test_ceq(self):
        self.gcc_machine.ldc(14)
        self.gcc_machine.ldc(4)
        self.gcc_machine.ceq()
        self.assertEquals(self.gcc_machine.data_stack, [0])
        self.gcc_machine.ldc(4)
        self.gcc_machine.ldc(4)
        self.gcc_machine.ceq()
        self.assertEquals(self.gcc_machine.data_stack, [0, 1])

    def test_cgt(self):
        self.gcc_machine.ldc(3)
        self.gcc_machine.ldc(4)
        self.gcc_machine.cgt()
        self.assertEquals(self.gcc_machine.data_stack, [0])
        self.gcc_machine.ldc(14)
        self.gcc_machine.ldc(4)
        self.gcc_machine.cgt()
        self.assertEquals(self.gcc_machine.data_stack, [0, 1])

    def test_cgte(self):
        self.gcc_machine.ldc(3)
        self.gcc_machine.ldc(4)
        self.gcc_machine.cgte()
        self.assertEquals(self.gcc_machine.data_stack, [0])
        self.gcc_machine.ldc(14)
        self.gcc_machine.ldc(4)
        self.gcc_machine.cgte()
        self.assertEquals(self.gcc_machine.data_stack, [0, 1])
        self.gcc_machine.ldc(4)
        self.gcc_machine.ldc(4)
        self.gcc_machine.cgte()
        self.assertEquals(self.gcc_machine.data_stack, [0, 1, 1])

    def test_cons(self):
        self.gcc_machine.ldc(3)
        self.gcc_machine.ldc(4)
        self.gcc_machine.cons()
        self.assertEquals(self.gcc_machine.data_stack, [(3, 4)])

    def test_atom(self):
        self.gcc_machine.ldc(3)
        self.gcc_machine.atom()
        self.assertEquals(self.gcc_machine.data_stack, [1])
        self.gcc_machine.ldc(4)
        self.gcc_machine.cons()
        self.gcc_machine.atom()
        self.assertEquals(self.gcc_machine.data_stack, [0])

    def test_car(self):
        self.gcc_machine.ldc(3)
        self.gcc_machine.ldc(4)
        self.gcc_machine.cons()
        self.gcc_machine.car()
        self.assertEquals(self.gcc_machine.data_stack, [3])

    def test_cdr(self):
        self.gcc_machine.ldc(3)
        self.gcc_machine.ldc(4)
        self.gcc_machine.cons()
        self.gcc_machine.cdr()
        self.assertEquals(self.gcc_machine.data_stack, [4])

    def test_parser(self):
        machine = GccMachine(parse_gcc("ldc 3\nldc 4\nadd"))
        machine.run()
        self.assertEquals(machine.data_stack, [7])

    def test_call(self):
        code = open("../data/lms/miner.gcc").read()
        machine = GccMachine(parse_gcc(code))
        state, step = machine.call(0, 0, 0)
        new_state, direction = machine.call(step, state, 0)
        self.assertEquals(2, direction)

    def test_max_ticks(self):
        code = open("../data/lms/miner.gcc").read()
        machine = GccMachine(parse_gcc(code))
        self.assertRaises(GccException, lambda: machine.call(0, 0, 0, max_ticks=3))

    def test_signed_32bit(self):
        self.gcc_machine.ldc(0xFFFFFFFF)
        self.gcc_machine.ldc(2)
        self.gcc_machine.mul()
        self.assertEquals(self.gcc_machine.data_stack, [-2])

