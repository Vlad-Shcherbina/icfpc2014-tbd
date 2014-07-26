from unittest import TestCase
from gcc_ast import *

class GccASTTest(TestCase):
    def test_constant(self):
        blk = GccCodeBlock()
        blk.instructions.append(GccConstant(3))
        builder = GccTextBuilder()
        blk.emit(builder, None)
        self.assertEquals("ldc 3\n", builder.text)

    def test_add(self):
        c1 = GccConstant(3)
        c2 = GccConstant(4)
        expr = GccAdd(c1, c2)
        blk = GccCodeBlock()
        blk.instructions.append(expr)
        builder = GccTextBuilder()
        blk.emit(builder, None)
        self.assertEquals("ldc 3\nldc 4\nadd\n", builder.text)

    def test_function(self):
        builder = GccTextBuilder()
        body = GccFunction("body", ["x"])
        var_ref = GccVariableReference("x")
        expr = GccAdd(var_ref, var_ref)
        body.add_instruction(expr)
        body.emit(builder)
        self.assertEquals("ld 0 0\nld 0 0\nadd\nrtn\n", builder.text)

    def test_function_reference(self):
        program = GccProgram()
        body = program.add_function("main", ["x"])
        body.add_instruction(GccFunctionReference("step"))
        program.add_function("step", ["x"])
        builder = GccTextBuilder()
        program.emit(builder)
        self.assertEquals("""ldf 2
rtn
rtn
""", builder.text)


    def test_function_call(self):
        program = GccProgram()

        main = program.add_function("main", [])
        main.add_instruction(GccCall(GccFunctionReference("body"), [GccConstant(21)]))

        body = program.add_function("body", ["x"])
        var_ref = GccVariableReference("x")
        body.add_instruction(GccAdd(var_ref, var_ref))

        builder = GccTextBuilder()
        program.emit(builder)

        self.assertEquals("""ldc 21
ldf 4
ap 1
rtn
ld 0 0
ld 0 0
add
rtn
""", builder.text)

    def test_conditional_expression(self):
        program = GccProgram()
        body = program.add_function("main", ["x"])
        var_ref = GccVariableReference("x")
        conditional_block = GccConditionalBlock(GccGt(var_ref, GccConstant(0)))
        conditional_block.true_branch.instructions.append(GccConstant(1))
        conditional_block.false_branch.instructions.append(GccConstant(0))
        body.add_instruction(conditional_block)
        builder = GccTextBuilder()
        program.emit(builder)
        self.assertEquals("""ld 0 0
ldc 0
gt
sel 5 7
rtn
ldc 1
join
ldc 0
join
""", builder.text)

    def test_tuple(self):
        program = GccProgram()
        body = program.add_function("main", ["x"])
        body.add_instruction(GccTuple(GccVariableReference("x"), GccConstant(1)))
        builder = GccTextBuilder()
        program.emit(builder)
        self.assertEquals("""ld 0 0
ldc 1
cons
rtn
""", builder.text)

    def test_tuple_member(self):
        program = GccProgram()
        body = program.add_function("main", ["x"])
        body.add_instruction(GccTupleMember(GccVariableReference("x"), 1, 3))
        builder = GccTextBuilder()
        program.emit(builder)
        self.assertEquals("""ld 0 0
cdr
car
rtn
""", builder.text)
