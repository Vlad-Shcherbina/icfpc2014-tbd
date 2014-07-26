class GccTextBuilder(object):
    def __init__(self):
        self.text = ""

    def fixup_pending_references(self):
        pass


class GccProgram(object):
    def __init__(self):
        self.functions = []

    def add_function(self, name, args):
        result = GccFunction(name, args)
        self.functions.append(result)
        return result

    def emit(self, builder):
        for f in self.functions:
            f.emit(builder)
        builder.fixup_pending_references()


class GccCodeBlock(object):
    def __init__(self):
        self.instructions = []


class GccFunction():
    def __init__(self, name, args):
        self.name = name
        self.args = args
        self.main_block = GccCodeBlock()

    def add_instruction(self, insn):
        self.main_block.instructions.append(insn)

    def emit(self, builder):
        pass


class GccConstant(object):
    def __init__(self, value):
        self.value = value

    def emit(self, target_block):
        target_block.instructions.append("ldc {0}".format(self.value))


class GccBinaryOp(object):
    def __init__(self, op1, op2, instruction):
        self.instruction = instruction
        self.op1 = op1
        self.op2 = op2

    def emit(self, target_block):
        self.op1.emit(target_block)
        self.op2.emit(target_block)
        target_block.instructions.append(self.instruction)


class GccAdd(GccBinaryOp):
    def __init__(self, op1, op2):
        super(GccAdd, self).__init__(op1, op2, "add")


class GccGt(GccBinaryOp):
    def __init__(self, op1, op2):
        super(GccGt, self).__init__(op1, op2, "gt")


class GccVariableReference(object):
    def __init__(self, name):
        self.name = name


class GccCall(object):
    def __init__(self, callee, args):
        self.callee = callee
        self.args = args


class GccConditionalBlock(object):
    def __init__(self, condition):
        self.condition = condition
        self.true_branch = GccCodeBlock()
        self.false_branch = GccCodeBlock()


class GccTuple(object):
    def __init__(self, *members):
        self.members = members


class GccTupleMember(object):
    def __init__(self, tuple, index, expected_size):
        self.tuple = tuple
        self.index = index
        self.expected_size = expected_size


class GccFunctionReference(object):
    def __init__(self, name):
        self.name = name
