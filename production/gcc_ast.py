class GccTextBuilder(object):
    def __init__(self):
        self.lines = []
        self.labels = {}

    @property
    def text(self):
        result = ''
        for i, line in enumerate(self.lines):
            for k, v in self.labels.items():
                if i == v:
                    result += ';{}\n'.format(k)
            result += '    ' + line + '\n'
        return result

    def add_instruction(self, name, *args):
        line = name
        if args:
            line += " " + " ".join(map(str, args))
        self.lines.append(line)

    def add_label(self, name):
        if name in self.labels:
            raise Exception("duplicate label " + name)
        self.labels[name] = len(self.lines)

    def allocate_label(self):
        name = "$label_{0}$".format(len(self.labels))
        self.labels[name] = None
        return name

    def resolve_label(self, name):
        if not name in self.labels:
            raise Exception("resolving label that wasn't created: " + name)
        self.labels[name] = len(self.lines)

    def fixup_labels(self):
        def fixup_labels_in_line(line):
            for name, offset in self.labels.iteritems():
                if offset is None:
                    raise Exception("Unresolved label " + name)
                if name in line:
                    line = line.replace(name, str(offset))
                    if name.startswith('$func_'):
                        line += '  ; {}'.format(name)
            return line

        self.lines = map(fixup_labels_in_line, self.lines)


class GccProgram(object):
    def __init__(self):
        self.functions = []
        self.function_index = {}

    def add_function(self, name, args):
        if name in self.function_index:
            raise Exception("duplicate function " + name)
        result = GccFunction(self, name, args)
        self.functions.append(result)
        self.function_index[name] = result
        return result

    def add_standard_main_function(self):
        f = self.add_function('main', ['world', 'undocumented'])
        f.add_instruction(GccInline("""
            DUM  2        ; 2 top-level declarations
            LDC  2        ; declare constant down
            LDF  $func_step$     ; declare function step
            LDF  $func_init$     ; init function
            RAP  2        ; load declarations into environment and run init
            """))
        # no need for return, it will be added automatically

    def emit(self, builder):
        for f in self.functions:
            builder.add_label("$func_{}$".format(f.name))
            f.emit(builder)
        builder.fixup_labels()


class GccCodeBlock(object):
    def __init__(self):
        self.instructions = []

    def emit(self, builder, context):
        for insn in self.instructions:
            insn.emit(builder, context)


class GccEmitContext(object):
    def __init__(self, function):
        self.function = function
        self.block_queue = []

    def resolve_variable(self, name):
        index = self.function.args.index(name)
        return 0, index

    def resolve_function(self, name):
        if not self.function.program:
            return None
        return self.function.program.function_index.get(name, None)

    def enqueue_block(self, block, label, terminator):
        self.block_queue.append((block, label, terminator))

    def resolve_queue(self, builder):
        while self.block_queue:
            # We can get additional blocks enqueued while generating this one.
            block, label, terminator = self.block_queue[0]
            del self.block_queue[0]
            builder.resolve_label(label)
            block.emit(builder, self)
            if terminator:
                builder.add_instruction(terminator)


class GccFunction():
    def __init__(self, program, name, args):
        self.program = program
        self.name = name
        self.args = args
        self.main_block = GccCodeBlock()

    def add_instruction(self, insn):
        self.main_block.instructions.append(insn)

    def emit(self, builder):
        context = GccEmitContext(self)
        self.main_block.emit(builder, context)
        builder.add_instruction('rtn')
        context.resolve_queue(builder)

class GccInline(object):
    def __init__(self, code):
        self.code = code

    def emit(self, builder, context):
        for line in self.code.strip().splitlines():
            builder.add_instruction(line.strip())

class GccConstant(object):
    def __init__(self, value):
        self.value = value

    def emit(self, builder, context):
        builder.add_instruction("ldc", self.value)


class GccBinaryOp(object):
    def __init__(self, op1, op2, instruction):
        self.instruction = instruction
        self.op1 = op1
        self.op2 = op2

    def emit(self, builder, context):
        self.op1.emit(builder, context)
        self.op2.emit(builder, context)
        builder.add_instruction(self.instruction)


class GccAdd(GccBinaryOp):
    def __init__(self, op1, op2):
        super(GccAdd, self).__init__(op1, op2, "add")


class GccSub(GccBinaryOp):
    def __init__(self, op1, op2):
        super(GccSub, self).__init__(op1, op2, "sub")


class GccMul(GccBinaryOp):
    def __init__(self, op1, op2):
        super(GccMul, self).__init__(op1, op2, "mul")


class GccDiv(GccBinaryOp):
    def __init__(self, op1, op2):
        super(GccDiv, self).__init__(op1, op2, "div")


class GccEq(GccBinaryOp):
    def __init__(self, op1, op2):
        super(GccEq, self).__init__(op1, op2, "ceq")


class GccGt(GccBinaryOp):
    def __init__(self, op1, op2):
        super(GccGt, self).__init__(op1, op2, "cgt")


class GccGte(GccBinaryOp):
    def __init__(self, op1, op2):
        super(GccGte, self).__init__(op1, op2, "cgte")


class GccNameReference(object):
    def __init__(self, name):
        self.name = name

    def emit(self, builder, context):
        fn = context.resolve_function(self.name)
        if fn:
            builder.add_instruction("ldf", "$func_{}$".format(self.name))
        else:
            frame_index, var_index = context.resolve_variable(self.name)
            builder.add_instruction("ld", frame_index, var_index)


class GccCall(object):
    def __init__(self, callee, args):
        self.callee = callee
        self.args = args

    def emit(self, builder, context):
        for arg in self.args:
            arg.emit(builder, context)
        self.callee.emit(builder, context)
        builder.add_instruction("ap", len(self.args))


class GccConditionalBlock(object):
    def __init__(self, condition):
        self.condition = condition
        self.true_branch = GccCodeBlock()
        self.false_branch = GccCodeBlock()

    def emit(self, builder, context):
        self.condition.emit(builder, context)
        true_label = builder.allocate_label()
        false_label = builder.allocate_label()
        context.enqueue_block(self.true_branch, true_label, "join")
        context.enqueue_block(self.false_branch, false_label, "join")
        builder.add_instruction("sel", true_label, false_label)


class GccTuple(object):
    def __init__(self, *members):
        self.members = members

    def emit(self, builder, context):
        for m in self.members:
            m.emit(builder, context)
        for i in range(len(self.members)-1):
            builder.add_instruction("cons")


class GccTupleMember(object):
    def __init__(self, tuple, index, expected_size):
        self.tuple = tuple
        self.index = index
        self.expected_size = expected_size

    def emit(self, builder, context):
        self.tuple.emit(builder, context)
        for i in range(self.index):
            builder.add_instruction("cdr")
        if self.index < self.expected_size-1:
            builder.add_instruction("car")
