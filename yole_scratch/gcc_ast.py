class GccTextBuilder(object):
    def __init__(self):
        self.lines = []
        self.labels = {}

    @property
    def text(self):
        return "\n".join(self.lines) + "\n"

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
        name = "$label_{0}".format(len(self.labels))
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
                line = line.replace(name, str(offset))
            return line

        self.lines = map(fixup_labels_in_line, self.lines)


class GccProgram(object):
    def __init__(self):
        self.functions = []
        self.function_index = {}

    def add_function(self, name, args):
        if name in self.function_index:
            raise Exception("duplicate function " + name)
        result = GccFunction(name, args)
        self.functions.append(result)
        self.function_index[name] = result
        return result

    def emit(self, builder):
        for f in self.functions:
            builder.add_label("$func_" + f.name)
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
    def __init__(self, name, args):
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


class GccVariableReference(object):
    def __init__(self, name):
        self.name = name

    def emit(self, builder, context):
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


class GccFunctionReference(object):
    def __init__(self, name):
        self.name = name

    def emit(self, builder, context):
        builder.add_instruction("ldf", "$func_" + self.name)
