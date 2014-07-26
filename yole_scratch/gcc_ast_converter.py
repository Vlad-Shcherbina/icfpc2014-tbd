import sys
sys.path.append("../production")

from ast import *
from gcc_ast import *


def convert_python_to_gcc_ast(ast):
    if isinstance(ast, Num):
        return GccConstant(ast.n)

    if isinstance(ast, BinOp):
        left = convert_python_to_gcc_ast(ast.left)
        right = convert_python_to_gcc_ast(ast.right)
        if isinstance(ast.op, Add):
            return GccAdd(left, right)
        if isinstance(ast.op, Sub):
            return GccSub(left, right)
        if isinstance(ast.op, Mult):
            return GccMul(left, right)
        if isinstance(ast.op, Div):
            return GccDiv(left, right)
        raise Exception("Unsupported binary operation type {0}".format(ast.op))

    if isinstance(ast, Compare):
        if len(ast.comparators) != 1:
            raise Exception("Chained comparisons not supported")
        left = convert_python_to_gcc_ast(ast.left)
        right = convert_python_to_gcc_ast(ast.comparators[0])
        if isinstance(ast.ops[0], Gt):
            return GccGt(left, right)
        if isinstance(ast.ops[0], GtE):
            return GccGte(left, right)
        if isinstance(ast.ops[0], Eq):
            return GccEq(left, right)
        raise Exception("Unsupported compare operation type {0}".format(ast.op))

    raise Exception("Unsupported Python AST node type {0}".format(ast))
