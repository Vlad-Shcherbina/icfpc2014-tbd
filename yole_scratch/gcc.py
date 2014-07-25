import functools


class GccFrame:
    def __init__(self, parent, size):
        self.parent = parent
        self.values = [None] * size


class GccClosure:
    def __init__(self, ip, frame):
        self.ip = ip
        self.frame = frame

class GccMachine:
    def __init__(self):
        self.data_stack = []
        self.current_frame = None
        self.instructions = []
        self.control_stack = []
        self.ip = 0
        self.done = False

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
            raise Exception("CONTROL_MISMATCH")
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

    def fetch_frame(self, index):
        result = self.current_frame
        for i in range(index):
            result = result.parent
        return result

    def pop_int(self):
        result = self.data_stack.pop()
        if type(result) != int:
            raise Exception("TAG_MISMATCH")
        return result

    def pop_cons(self):
        result = self.data_stack.pop()
        if type(result) != tuple:
            raise Exception("TAG_MISMATCH")
        return result

    def pop_closure(self):
        closure = self.data_stack.pop()
        if not isinstance(closure, GccClosure):
            raise Exception("TAG_MISMATCH")
        return closure

    def add_instruction(self, name, args):
        fn = getattr(GccMachine, name)
        args = [self] + args
        f = functools.partial(fn, *args)
        f.instruction_name = name
        f.instruction_args = args
        self.instructions.append(f)

    def run(self):
        while self.ip >= 0 and self.ip < len(self.instructions):
            next_ip = self.instructions[self.ip]()
            if self.done:
                break
            if next_ip is not None:
                self.ip = next_ip
            else:
                self.ip = self.ip + 1


def parse_gcc(code):
    machine = GccMachine()
    for line in code.splitlines():
        semicolon = line.find(';')
        if semicolon >= 0:
            line = line[:semicolon]
        line = line.strip()
        if not line:
            continue
        fields = line.split()
        instruction = fields[0].lower()
        args = map(int, fields[1:])
        machine.add_instruction(instruction, args)

    return machine
