from unittest import TestCase
import ast

from gcc_ast_converter import *

class GccASTConverterTest(TestCase):
    def test_constant(self):
        x = ast.parse("3").body[0].value
        tree = convert_python_to_gcc_ast(x)
        self.assertIsInstance(tree, GccConstant)
        self.assertEquals(3, tree.value)

    def test_binary(self):
        x = ast.parse("3+4").body[0].value
        tree = convert_python_to_gcc_ast(x)
        self.assertIsInstance(tree, GccAdd)
        self.assertEquals(3, tree.op1.value)
        self.assertEquals(4, tree.op2.value)

    def test_compare(self):
        x = ast.parse("3>4").body[0].value
        tree = convert_python_to_gcc_ast(x)
        self.assertIsInstance(tree, GccGt)
        self.assertEquals(3, tree.op1.value)
        self.assertEquals(4, tree.op2.value)

    def test_less(self):
        x = ast.parse("3<4").body[0].value
        tree = convert_python_to_gcc_ast(x)
        self.assertIsInstance(tree, GccGt)
        self.assertEquals(4, tree.op1.value)
        self.assertEquals(3, tree.op2.value)

    def test_name(self):
        x = ast.parse("a-1").body[0].value
        tree = convert_python_to_gcc_ast(x)
        self.assertIsInstance(tree, GccSub)
        self.assertIsInstance(tree.op1, GccNameReference)
        self.assertEquals("a", tree.op1.name)

    def test_function(self):
        x = ast.parse("def main(world, ghosts): return 42")
        tree = convert_python_to_gcc_function(None, x.body[0])
        self.assertIsInstance(tree, GccFunction)
        self.assertEquals("main", tree.name)
        self.assertEquals(["world", "ghosts"], tree.args)
        self.assertIsInstance(tree.main_block.instructions[0], GccConstant)

    def test_tuple(self):
        x = ast.parse("(2, 3)").body[0].value
        tree = convert_python_to_gcc_ast(x)
        self.assertIsInstance(tree, GccTuple)
        self.assertEquals(2, tree.members[0].value)
        self.assertEquals(3, tree.members[1].value)

    def test_module(self):
        x = ast.parse("""
def main(world, ghosts): return 42, step
def step(state, world): return state+1, 2""")
        tree = convert_python_to_gcc_module(x)
        self.assertIsInstance(tree, GccProgram)
        builder = GccTextBuilder()
        tree.emit(builder)
        self.assertEquals(""";$func_main$
    LDC 42
    LDF 4  ; $func_step$
    CONS
    RTN
;$func_step$
    LD 0 0
    LDC 1
    ADD
    LDC 2
    CONS
    RTN
""", builder.text)
        self.assertEquals("IP 6 (at label $func_step$+2) (at source 3:31)",
                          builder.details_for_ip(6))

    def test_condition(self):
        x = ast.parse("""
def fetch_element(list, n):
    if n == 0:
        return 42
    else:
        return 239""")
        tree = convert_python_to_gcc_function(None, x.body[0])
        cond = tree.main_block.instructions[0]
        self.assertIsInstance(cond, GccConditionalBlock)
        self.assertEquals(42, cond.true_branch.instructions[0].value)
        self.assertEquals(239, cond.false_branch.instructions[0].value)

    def test_tuple_member(self):
        x = ast.parse("x[1]")
        tree = convert_python_to_gcc_ast(x.body[0].value)
        self.assertIsInstance(tree, GccTupleMember)
        self.assertEquals(1, tree.index)
        self.assertEquals(3, tree.expected_size)

    def test_cdr(self):
        x = ast.parse("x[1:]")
        tree = convert_python_to_gcc_ast(x.body[0].value)
        self.assertIsInstance(tree, GccTupleMember)
        self.assertEquals(1, tree.index)
        self.assertEquals(2, tree.expected_size)

    def test_call(self):
        x = ast.parse("""
def fetch_element(list, n):
    if n == 0:
        return x[0]
    else:
        return fetch_element(list, n-1)""")
        tree = convert_python_to_gcc_function(None, x.body[0])
        cond = tree.main_block.instructions[0]
        call = cond.false_branch.instructions[0]
        self.assertIsInstance(call, GccCall)
        self.assertEquals("fetch_element", call.callee.name)
        self.assertEquals("list", call.args[0].name)
        self.assertIsInstance(call.args[1], GccSub)

    def test_print(self):
        x = ast.parse("def f(x): print x")
        tree = convert_python_to_gcc_function(None, x.body[0])
        self.assertIsInstance(tree.main_block.instructions[0], GccPrint)

    def test_assignment(self):
        x = ast.parse("def f(): x = 1")
        tree = convert_python_to_gcc_function(None, x.body[0])
        assignment = tree.main_block.instructions[0]
        self.assertIsInstance(assignment, GccAssignment)
        self.assertEquals("x", assignment.name)

    def test_atom(self):
        x = ast.parse("from intrinsics import nil\ndef f(x): nil(x)")
        tree = convert_python_to_gcc_module(x)
        call = tree.functions[0].main_block.instructions[0]
        self.assertIsInstance(call, GccIntrinsic)
        self.assertEquals("nil", call.name)
        self.assertEquals("x", call.arg.name)

    def test_nested_function(self):
        x = ast.parse("""
def f(x):
    def nested():
        return x
    return nested""")
        tree = convert_python_to_gcc_function(None, x.body[0])
        self.assertEquals("nested", tree.nested_functions[0].name)
