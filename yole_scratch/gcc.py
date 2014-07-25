import functools


class GCCFrame:
    def __init__(self, parent, size):
        self.parent = parent
        self.values = [None] * size

class GCCMachine:
    def __init__(self):
        self.data_stack = []
        self.current_frame = None
        self.instructions = []
        self.ip = 0

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

    def dum(self, arg):
        self.current_frame = GCCFrame(self.current_frame, arg)

    def st(self, arg, arg2):
        self.fetch_frame(arg).values[arg2] = self.data_stack.pop()

    def ld(self, arg, arg2):
        self.data_stack.append(self.fetch_frame(arg).values[arg2])

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

    def run(self):
        while self.ip >= 0 and self.ip < len(self.instructions):
            next_ip = self.instructions[self.ip]()
            if next_ip is not None:
                self.ip = next_ip
            else:
                self.ip = self.ip + 1

def parse_gcc(code):
    machine = GCCMachine()
    for line in code.splitlines():
        semicolon = line.find(';')
        if semicolon >= 0:
            line = line[:semicolon]
        line = line.strip()
        if not line:
            continue
        fields = line.split(' ')
        instruction = fields[0].lower()
        fn = getattr(GCCMachine, instruction)
        args = [machine] + map(int, fields[1:])
        f = functools.partial(fn, *args)
        f.text = line
        machine.instructions.append(f)

    return machine
