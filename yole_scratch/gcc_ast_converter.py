import sys
sys.path.append("../production")

from ast import *
from gcc_ast import *


def convert_python_to_gcc_module(module):
    program = GccProgram()
    for node in module.body:
        if isinstance(node, FunctionDef):
            convert_python_to_gcc_function(program, node)
        else:
            raise Exception("Unsupported module child type {0}".format(node))
    return program


def convert_python_to_gcc_function(program, func_def):
    args = [a.id for a in func_def.args.args]
    if program:
        func = program.add_function(func_def.name, args)
    else:
        func = GccFunction(None, func_def.name, args)
    for stmt in func_def.body:
        if isinstance(stmt, Expr) or isinstance(stmt, Return):
            func.add_instruction(convert_python_to_gcc_ast(stmt.value))
        else:
            raise Exception("Unsupported statement type {0}".format(stmt))
    return func


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

    if isinstance(ast, Name):
        return GccNameReference(ast.id)

    if isinstance(ast, Tuple):
        return GccTuple(*[convert_python_to_gcc_ast(elt) for elt in ast.elts])

    raise Exception("Unsupported Python AST node type {0}".format(ast))
