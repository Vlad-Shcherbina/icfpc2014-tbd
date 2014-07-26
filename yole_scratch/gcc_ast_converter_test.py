from unittest import TestCase
import ast

import sys
sys.path.append('../production')

from gcc_ast import *
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
def main(world, ghosts): return 42, step\n
def step(state, world): return state+1, 2""")
        tree = convert_python_to_gcc_module(x)
        self.assertIsInstance(tree, GccProgram)
        builder = GccTextBuilder()
        tree.emit(builder)
        self.assertEquals(""";$func_main$
    ldc 42
    ldf 4  ; $func_step$
    cons
    rtn
;$func_step$
    ld 0 0
    ldc 1
    add
    ldc 2
    cons
    rtn
""", builder.text)
