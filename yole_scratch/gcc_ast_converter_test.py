from unittest import TestCase
import ast

import sys
sys.path.append('../production')

from gcc_ast import *
from gcc_ast_converter import convert_python_to_gcc_ast

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
