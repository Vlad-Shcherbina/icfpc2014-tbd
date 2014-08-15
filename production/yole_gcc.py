import functools
from gcc_wrapper import GCCInterface
from gcc_utils import deep_unmarshal, deep_marshal


class GccException(Exception):
    def __init__(self, *args, **kwargs):
        super(GccException, self).__init__(*args, **kwargs)


class GccFrame:
    def __init__(self, parent, size, dummy=False):
        self.parent = parent
        self.values = [None] * size
        self.dummy = dummy


class GccClosure:
    def __init__(self, ip, frame):
        self.ip = ip
        self.frame = frame


def to_int32(x):
    return int((x & 0xFFFFFFFF) - ((x & 0x80000000) << 1))


class GccMachine(GCCInterface):
    def __init__(self, instructions=None, source_map=None):
        self.data_stack = []
        self.current_frame = None
        self.instructions = []
        self.control_stack = []
        self.ip = 0
        if instructions:
            for insn in instructions:
                self.add_instruction(insn.op.lower(), insn.args)
        self.source_map = source_map

    def marshal(self, x):
        if isinstance(x, (int, long)):
            return  to_int32(x)
        return x

    def unmarshal(self, x):
        return x


    def call(self, address_or_closure, *args, **kwargs):
        assert len(self.data_stack) == 0
        if not isinstance(address_or_closure, GccClosure):
            address_or_closure = GccClosure(address_or_closure, None)
        callee_frame = GccFrame(address_or_closure.frame, len(args))
        for i in range(len(args)):
            callee_frame.values[i] = deep_marshal(self.marshal, args[i])
        self.current_frame = callee_frame
        self.ip = address_or_closure.ip
        self.run(kwargs.get('max_ticks'))
        assert len(self.data_stack) == 1
        return deep_unmarshal(self.unmarshal, self.data_stack.pop())

    def brk(self, arg):
        self.pop()

    def ldc(self, arg):
        self.data_stack.append(to_int32(arg))

    def add(self):
        self.data_stack.append(to_int32(self.pop_int() + self.pop_int()))

    def sub(self):
        y = self.pop_int()
        x = self.pop_int()
        self.data_stack.append(to_int32(x - y))

    def mul(self):
        self.data_stack.append(to_int32(self.pop_int() * self.pop_int()))

    def div(self):
        y = self.pop_int()
        x = self.pop_int()
        self.data_stack.append(to_int32(x // y))


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

    def tsel(self, arg_true, arg_false):
        x = self.pop_int()
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
        self.current_frame = GccFrame(self.current_frame, arg, True)

    def st(self, arg, arg2):
        frame = self.fetch_frame(arg)
        if frame.dummy:
            raise GccException("FRAME_MISMATCH: can't store into dummy frame")
        frame.values[arg2] = self.data_stack.pop()

    def ld(self, arg, arg2):
        frame = self.fetch_frame(arg)
        if frame.dummy:
            raise GccException("FRAME_MISMATCH: can't load from dummy frame")
        self.data_stack.append(frame.values[arg2])

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

    def tap(self, arg):
        closure = self.pop_closure()
        callee_frame = GccFrame(closure.frame, arg)
        for i in range(arg-1, -1, -1):
            callee_frame.values[i] = self.data_stack.pop()
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
        return self.do_recursive_call(arg, False)

    def trap(self, arg):
        return self.do_recursive_call(arg, True)

    def do_recursive_call(self, argc, tailcall):
        closure = self.pop_closure()
        if not closure.frame.dummy:
            raise GccException("FRAME_MISMATCH (RAP with non-DUM frame)")
        if len(closure.frame.values) != argc:
            raise GccException("FRAME_MISMATCH (wrong argument count)")
        if closure.frame != self.current_frame:
            raise GccException("FRAME_MISMATCH")
        for i in range(argc-1, -1, -1):
            closure.frame.values[i] = self.data_stack.pop()
        if not tailcall:
            self.control_stack.append((self.current_frame.parent, self.ip+1))
        closure.frame.dummy = False
        return closure.ip

    def dbug(self):
        print str(self.data_stack.pop())

    def fetch_frame(self, index):
        result = self.current_frame
        for i in range(index):
            result = result.parent
        return result

    def pop_int(self):
        if not self.data_stack:
            raise GccException("pop int from empty stack")
        result = self.data_stack.pop()
        if type(result) != int:
            raise GccException("TAG_MISMATCH: Expected int, found " +
                               str(result))
        return result

    def pop_cons(self):
        if not self.data_stack:
            raise GccException("pop cons cell from empty stack")
        result = self.data_stack.pop()
        if type(result) != tuple:
            raise GccException("TAG_MISMATCH: Expected cons cell, found " +
                            str(result))
        return result

    def pop_closure(self):
        if not self.data_stack:
            raise GccException("pop closure from empty stack")
        closure = self.data_stack.pop()
        if not isinstance(closure, GccClosure):
            raise GccException("TAG_MISMATCH: Expected closure, found " +
                               str(closure))
        return closure

    def add_instruction(self, name, args):
        fn = getattr(GccMachine, name)
        call_args = [self] + args
        f = functools.partial(fn, *call_args)
        f.instruction_name = name
        f.instruction_args = args
        self.instructions.append(f)

    def run(self, max_ticks=None):
        if len(self.instructions) > 1048576:
            raise GccException("Program too long")
        self.done = False
        self.ticks = 0
        while self.ip >= 0 and self.ip < len(self.instructions):
            self.ticks += 1
            if max_ticks and self.ticks > max_ticks:
                raise GccException("Execution time limit exceeded")

            try:
                next_ip = self.instructions[self.ip]()
            except GccException, e:
                if self.source_map:
                    location = self.format_stacktrace()
                else:
                    location = "at IP " + str(self.ip)
                raise GccException("Error: {1} at {2} {3}\n{0}\n{4}".format(
                    location, e.message,
                    self.instructions[self.ip].instruction_name,
                    self.instructions[self.ip].instruction_args,
                    self.format_frames()))

            if self.done:
                break
            if next_ip is not None:
                self.ip = next_ip
            else:
                self.ip = self.ip + 1

    def format_stacktrace(self):
        result = "  at " + self.source_map.details_for_ip(self.ip)
        for caller in self.control_stack[::-1]:
            if type(caller) == tuple:
                caller = caller[1]
                result += "\n  at " + self.source_map.details_for_ip(caller)
        return result

    def format_frames(self):
        result = "Frames:\n"
        f = self.current_frame
        while f:
            result += "  " + str(f.values) + "\n"
            f = f.parent
        return result

    def last_call_ticks(self):
        return self.ticks
