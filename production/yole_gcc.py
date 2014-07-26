import functools
from gcc_wrapper import GCCInterface


class GccException(Exception):
    def __init__(self, *args, **kwargs):
        super(GccException, self).__init__(*args, **kwargs)


class GccFrame:
    def __init__(self, parent, size):
        self.parent = parent
        self.values = [None] * size


class GccClosure:
    def __init__(self, ip, frame):
        self.ip = ip
        self.frame = frame

class GccMachine(GCCInterface):
    def __init__(self, instructions=None):
        self.data_stack = []
        self.current_frame = None
        self.instructions = []
        self.control_stack = []
        self.ip = 0
        if instructions:
            for insn in instructions:
                self.add_instruction(insn.op.lower(), insn.args)

    def marshall_int(self, i):
        return i

    def marshall_cons(self, car, cdr):
        return car, cdr

    def call(self, address_or_closure, *args):
        assert len(self.data_stack) == 0
        if not isinstance(address_or_closure, GccClosure):
            address_or_closure = GccClosure(address_or_closure, None)
        callee_frame = GccFrame(address_or_closure.frame, len(args))
        for i in range(len(args)):
            callee_frame.values[i] = args[i]
        self.current_frame = callee_frame
        self.ip = address_or_closure.ip
        self.run()
        if self.data_stack:
            assert len(self.data_stack) == 1
            result = self.data_stack[0]
            self.data_stack = []
            return result

    def ldc(self, arg):
        self.data_stack.append(arg)

    def add(self):
        self.data_stack.append(self.pop_int() + self.pop_int())

    def sub(self):
        y = self.pop_int()
        x = self.pop_int()
        self.data_stack.append(x - y)

    def mul(self):
        self.data_stack.append(self.pop_int() * self.pop_int())

    def div(self):
        y = self.pop_int()
        x = self.pop_int()
        self.data_stack.append(x // y)

    def ceq(self):
        self.data_stack.append(1 if self.pop_int() == self.pop_int() else 0)

    def cgt(self):
        y = self.pop_int()
        x = self.pop_int()
        self.data_stack.append(1 if x > y else 0)

    def cgte(self):
        y = self.pop_int()
        x = self.pop_int()
        self.data_stack.append(1 if x >= y else 0)

    def atom(self):
        x = self.data_stack.pop()
        self.data_stack.append(1 if type(x) == int else 0)

    def cons(self):
        y = self.data_stack.pop()
        x = self.data_stack.pop()
        self.data_stack.append((x, y))

    def car(self):
        self.data_stack.append(self.pop_cons()[0])

    def cdr(self):
        self.data_stack.append(self.pop_cons()[1])

    def sel(self, arg_true, arg_false):
        x = self.pop_int()
        self.control_stack.append(self.ip+1)
        if x == 0:
            return arg_false
        else:
            return arg_true

    def join(self):
        ip = self.control_stack.pop()
        if type(ip) != int:
            raise GccException("CONTROL_MISMATCH")
        return ip

    def dum(self, arg):
        self.current_frame = GccFrame(self.current_frame, arg)

    def st(self, arg, arg2):
        self.fetch_frame(arg).values[arg2] = self.data_stack.pop()

    def ld(self, arg, arg2):
        self.data_stack.append(self.fetch_frame(arg).values[arg2])

    def ldf(self, arg):
        self.data_stack.append(GccClosure(arg, self.current_frame))

    def ap(self, arg):
        closure = self.pop_closure()
        callee_frame = GccFrame(closure.frame, arg)
        for i in range(arg-1, -1, -1):
            callee_frame.values[i] = self.data_stack.pop()
        self.control_stack.append((self.current_frame, self.ip+1))
        self.current_frame = callee_frame
        return closure.ip

    def rtn(self):
        if not self.control_stack:
            self.done = True
            return
        frame, ip = self.control_stack.pop()
        self.current_frame = frame
        return ip

    def rap(self, arg):
        closure = self.pop_closure()
        if closure.frame != self.current_frame:
            raise GccException("FRAME_MISMATCH")
        for i in range(arg-1, -1, -1):
            closure.frame.values[i] = self.data_stack.pop()
        self.control_stack.append((self.current_frame.parent, self.ip+1))
        return closure.ip

    def fetch_frame(self, index):
        result = self.current_frame
        for i in range(index):
            result = result.parent
        return result

    def pop_int(self):
        result = self.data_stack.pop()
        if type(result) != int:
            raise GccException("TAG_MISMATCH")
        return result

    def pop_cons(self):
        result = self.data_stack.pop()
        if type(result) != tuple:
            raise GccException("TAG_MISMATCH: Expected cons cell, found " +
                            str(result))
        return result

    def pop_closure(self):
        closure = self.data_stack.pop()
        if not isinstance(closure, GccClosure):
            raise GccException("TAG_MISMATCH")
        return closure

    def add_instruction(self, name, args):
        fn = getattr(GccMachine, name)
        args = [self] + args
        f = functools.partial(fn, *args)
        f.instruction_name = name
        f.instruction_args = args
        self.instructions.append(f)

    def run(self):
        self.done = False
        while self.ip >= 0 and self.ip < len(self.instructions):
            try:
                next_ip = self.instructions[self.ip]()
            except GccException, e:
                raise GccException("Error at IP {0}: {1}".format(
                    self.ip, e.message))

            if self.done:
                break
            if next_ip is not None:
                self.ip = next_ip
            else:
                self.ip = self.ip + 1
