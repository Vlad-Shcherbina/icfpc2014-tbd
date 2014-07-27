class GccSyntaxError(Exception):
    pass


class GccTextBuilder(object):
    def __init__(self):
        self.lines = []
        self.labels = {}
        self.source_locations = []

    @property
    def text(self):
        result = ''
        for i, line in enumerate(self.lines):
            for k, v in self.labels.items():
                if i == v:
                    result += ';{}\n'.format(k)
            result += '    ' + line + '\n'
        return result

    def add_instruction(self, name, *args, **kwargs):
        line = name.upper()
        if args:
            line += " " + " ".join(map(str, args))
        self.lines.append(line)
        self.source_locations.append(kwargs.get('source'))

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

    def details_for_ip(self, ip):
        previous_label_ip = -1
        label_name = None
        for name, offset in self.labels.iteritems():
            if name.startswith("$label"):
                continue
            if ip > offset > previous_label_ip:
                label_name = name
                previous_label_ip = offset
        result = "IP {0}".format(ip)
        if label_name:
            result += " (at label {0}+{1})".format(label_name,
                                                   ip-previous_label_ip)
        source = self.source_locations[ip]
        if source:
            result += " (at source {0}:{1})".format(source[0], source[1])
        return result


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

    def emit(self, builder, **kwargs):
        for f in self.functions:
            builder.add_label("$func_{}$".format(f.name))
            f.emit(builder, **kwargs)
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
        self.terminated = False
        self.disable_tco = False

    def resolve_variable(self, name):
        args_frame_index = 0
        if self.function.local_variables:
            try:
                return 0, self.function.local_variables.index(name)
            except ValueError:
                pass  # ignore, continue lookup
            args_frame_index += 1
        index = self.function.args.index(name)
        return args_frame_index, index

    def resolve_function(self, name):
        if not self.function.program:
            return None
        return self.function.program.function_index.get(name, None)

    def enqueue_block(self, block, label, terminator):
        self.block_queue.append((block, label, terminator))

    def resolve_queue(self, builder):
        while self.block_queue:
            # We can get additional blocks enqueued while generating this one.
            self.terminated = False
            block, label, terminator = self.block_queue[0]
            del self.block_queue[0]
            builder.resolve_label(label)
            block.emit(builder, self)
            if terminator and not self.terminated:
                builder.add_instruction(terminator)

    def is_tail(self, instruction):
        if self.disable_tco: return False
        return self.is_block_tail(instruction, self.function.main_block)

    def is_block_tail(self, instruction, block):
        if not block.instructions: return False
        last_insn = block.instructions[-1]
        if last_insn == instruction:
            return True
        if isinstance(last_insn, GccConditionalBlock):
            return (self.is_block_tail(instruction, last_insn.true_branch) or
                    self.is_block_tail(instruction, last_insn.false_branch))
        return False


class GccASTNode(object):
    def __init__(self):
        self.source_location = None


class GccFunction(GccASTNode):
    def __init__(self, program, name, args):
        GccASTNode.__init__(self)
        self.program = program
        self.name = name
        self.args = args
        self.main_block = GccCodeBlock()
        self.local_variables = []

    def add_instruction(self, insn):
        self.main_block.instructions.append(insn)

    def emit(self, builder, **kwargs):
        context = GccEmitContext(self)
        if 'disable_tco' in kwargs:
            context.disable_tco = True
        self.collect_local_variables(self.main_block, context)
        if self.program:
            self.check_name_conflicts()
        if self.local_variables:
            builder.add_instruction("dum", len(self.local_variables))
            for i in range(len(self.local_variables)):
                builder.add_instruction("ldc", 0)
            locals_frame_label = "$func_locals_" + self.name + "$"
            builder.add_instruction("ldf", locals_frame_label)
            builder.add_instruction("trap", len(self.local_variables))
            builder.add_label(locals_frame_label)
        self.main_block.emit(builder, context)
        if not context.terminated:
            builder.add_instruction('rtn')
        context.resolve_queue(builder)

    def collect_local_variables(self, block, context):
        for insn in block.instructions:
            if isinstance(insn, GccAssignment):
                try:
                    context.resolve_variable(insn.name)
                except ValueError:
                    self.local_variables.append(insn.name)
            elif isinstance(insn, GccConditionalBlock):
                self.collect_local_variables(insn.true_branch, context)
                self.collect_local_variables(insn.false_branch, context)

    def check_name_conflicts(self):
        for arg in self.args:
            if arg in self.program.function_index:
                raise GccSyntaxError("Name conflict (arg/function): " + arg)

        for local in self.local_variables:
            if local in self.program.function_index:
                raise GccSyntaxError("Name conflict (local/function): " + local)

class GccInline(object):
    def __init__(self, code):
        self.code = code

    def emit(self, builder, context):
        for line in self.code.strip().splitlines():
            builder.add_instruction(line.strip())


class GccConstant(GccASTNode):
    def __init__(self, value):
        GccASTNode.__init__(self)
        self.value = value

    def emit(self, builder, context):
        builder.add_instruction("ldc", self.value, source=self.source_location)


class GccBinaryOp(GccASTNode):
    def __init__(self, op1, op2, instruction):
        GccASTNode.__init__(self)
        self.instruction = instruction
        self.op1 = op1
        self.op2 = op2

    def emit(self, builder, context):
        self.op1.emit(builder, context)
        self.op2.emit(builder, context)
        builder.add_instruction(self.instruction, source=self.source_location)


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


class GccNameReference(GccASTNode):
    def __init__(self, name):
        super(GccNameReference, self).__init__()
        self.name = name

    def emit(self, builder, context):
        fn = context.resolve_function(self.name)
        if fn:
            builder.add_instruction("ldf", "$func_{}$".format(self.name),
                                    source=self.source_location)
        else:
            frame_index, var_index = context.resolve_variable(self.name)
            builder.add_instruction("ld", frame_index, var_index,
                                    source=self.source_location)


class GccCall(GccASTNode):
    def __init__(self, callee, args):
        super(GccCall, self).__init__()
        self.callee = callee
        self.args = args

    def emit(self, builder, context):
        for arg in self.args:
            arg.emit(builder, context)
        self.callee.emit(builder, context)
        if context.is_tail(self):
            context.terminated = True
            insn_name = "tap"
        else:
            insn_name = "ap"
        builder.add_instruction(insn_name, len(self.args),
                                source=self.source_location)


class GccConditionalBlock(GccASTNode):
    def __init__(self, condition):
        super(GccConditionalBlock, self).__init__()
        self.condition = condition
        self.true_branch = GccCodeBlock()
        self.false_branch = GccCodeBlock()

    def emit(self, builder, context):
        self.condition.emit(builder, context)
        true_label = builder.allocate_label()
        false_label = builder.allocate_label()
        if context.is_tail(self):
            instruction = "tsel"
            terminator = "rtn"
            context.terminated = True
        else:
            instruction = "sel"
            terminator = "join"
        context.enqueue_block(self.true_branch, true_label, terminator)
        context.enqueue_block(self.false_branch, false_label, terminator)
        builder.add_instruction(instruction, true_label, false_label,
                                source=self.source_location)


class GccTuple(GccASTNode):
    def __init__(self, *members):
        super(GccTuple, self).__init__()
        self.members = members

    def emit(self, builder, context):
        for m in self.members:
            m.emit(builder, context)
        for i in range(len(self.members)-1):
            builder.add_instruction("cons", source=self.source_location)


class GccTupleMember(GccASTNode):
    def __init__(self, tuple, index, expected_size):
        super(GccTupleMember, self).__init__()
        self.tuple = tuple
        self.index = index
        self.expected_size = expected_size

    def emit(self, builder, context):
        self.tuple.emit(builder, context)
        for i in range(self.index):
            builder.add_instruction("cdr", source=self.source_location)
        if self.index < self.expected_size-1:
            builder.add_instruction("car", source=self.source_location)


class GccPrint(GccASTNode):
    def __init__(self, arg):
        super(GccPrint, self).__init__()
        self.arg = arg

    def emit(self, builder, context):
        self.arg.emit(builder, context)
        builder.add_instruction("dbug", source=self.source_location)


class GccAssignment(GccASTNode):
    def __init__(self, name, value):
        super(GccAssignment, self).__init__()
        self.name = name
        self.value = value

    def emit(self, builder, context):
        self.value.emit(builder, context)
        frame_index, var_index = context.resolve_variable(self.name)
        builder.add_instruction("st", frame_index, var_index,
                                source=self.source_location)


class GccAtom(GccASTNode):
    def __init__(self, arg):
        super(GccAtom, self).__init__()
        self.arg = arg

    def emit(self, builder, context):
        self.arg.emit(builder, context)
        builder.add_instruction("atom", source=self.source_location)
