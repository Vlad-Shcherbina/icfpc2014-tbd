from ast import *
from gcc_ast import *


def convert_python_to_gcc_module(module):
    program = GccProgram()
    for node in module.body:
        if isinstance(node, FunctionDef):
            convert_python_to_gcc_function(program, node)
        elif isinstance(node, ImportFrom):
            print convert_python_to_gcc_import(program, node.module, node.names)
        else:
            raise Exception("Unsupported module child type {0}".format(node))
    return program


def convert_python_to_gcc_import(program, module, names):
    if module != 'intrinsics':
        raise Exception('Only import from intrinsics allowed: {}'.format(module))
    for it in names:
        if it.asname is not None:
            raise Exception('import ... as ... syntax not allowed {}'.format(it.asname))
        if it.name not in GccIntrinsic.variants:
            raise Exception('Unknown intrinsic: {}'.format(it.name))
        program.add_imported_intrinsic(it.name)


def convert_python_to_gcc_function(program, func_def, parent_function=None):
    args = [a.id for a in func_def.args.args]
    if parent_function:
        func = parent_function.add_nested_function(func_def.name, args)
    elif program:
        func = program.add_function(func_def.name, args)
    else:
        func = GccFunction(None, func_def.name, args)
    func.source_location = (func_def.lineno, func_def.col_offset)
    for stmt in func_def.body:
        if isinstance(stmt, FunctionDef):
            convert_python_to_gcc_function(program, stmt, func)
        else:
            func.add_instruction(convert_python_to_gcc_statement(stmt))
    return func


def convert_python_to_gcc_statement(stmt):
    if isinstance(stmt, Expr) or isinstance(stmt, Return):
        return convert_python_to_gcc_ast(stmt.value)

    if isinstance(stmt, If):
        test = convert_python_to_gcc_ast(stmt.test)
        cond = GccConditionalBlock(test)
        for child in stmt.body:
            if isinstance(child, Pass):
                continue
            cond.true_branch.instructions.append(
                convert_python_to_gcc_statement(child))
        for child in stmt.orelse:
            if isinstance(child, Pass):
                continue
            cond.false_branch.instructions.append(
                convert_python_to_gcc_statement(child))
        result = cond

    elif isinstance(stmt, Print):
        result = GccPrint(convert_python_to_gcc_ast(stmt.values[0]))

    elif isinstance(stmt, Assign):
        result = GccAssignment(stmt.targets[0].id,
                               convert_python_to_gcc_ast(stmt.value))
    elif isinstance(stmt, While):
        test = convert_python_to_gcc_ast(stmt.test)
        cond = GccWhileBlock(test)
        for child in stmt.body:
            if isinstance(child, Pass):
                continue
            cond.code.instructions.append(
                convert_python_to_gcc_statement(child))
        result = cond
    else:
        raise Exception("Unsupported statement type {0}".format(stmt))
    result.source_location = (stmt.lineno, stmt.col_offset)
    return result


def convert_python_to_gcc_ast(ast):
    if isinstance(ast, Num):
        if not isinstance(ast.n, (int, long)):
            raise Exception("Unsupported literal type: {} ({!r})".format(type(ast.n), ast.n))
        if ast.n < -2**31 - 1 or ast.n > 2**31:
            raise Exception("Integer literal out of range: {}".format(ast.n))
        result = GccConstant(ast.n)

    elif isinstance(ast, UnaryOp):
        operand = convert_python_to_gcc_ast(ast.operand)
        if isinstance(ast.op, Not):
            result = GccNot(operand)
        else:
            raise Exception("Unsupported binary operation type {0}".format(ast.op))
        
    elif isinstance(ast, BinOp):
        left = convert_python_to_gcc_ast(ast.left)
        right = convert_python_to_gcc_ast(ast.right)
        if isinstance(ast.op, Add):
            result = GccAdd(left, right)
        elif isinstance(ast.op, Sub):
            result = GccSub(left, right)
        elif isinstance(ast.op, Mult):
            result = GccMul(left, right)
        elif isinstance(ast.op, Div):
            result = GccDiv(left, right)
        else:
            raise Exception("Unsupported binary operation type {0}".format(ast.op))

    elif isinstance(ast, Compare):
        if len(ast.comparators) != 1:
            raise Exception("Chained comparisons not supported")
        left = convert_python_to_gcc_ast(ast.left)
        right = convert_python_to_gcc_ast(ast.comparators[0])
        if isinstance(ast.ops[0], Gt):
            result = GccGt(left, right)
        elif isinstance(ast.ops[0], GtE):
            result = GccGte(left, right)
        elif isinstance(ast.ops[0], Lt):
            result = GccGt(right, left)
        elif isinstance(ast.ops[0], LtE):
            result = GccGte(right, left)
        elif isinstance(ast.ops[0], Eq):
            result = GccEq(left, right)
        else:
            raise Exception("Unsupported compare operation type {0}".format(ast.ops[0]))

    elif isinstance(ast, Name):
        result = GccNameReference(ast.id)

    elif isinstance(ast, Tuple):
        result = GccTuple(*[convert_python_to_gcc_ast(elt) for elt in ast.elts])

    elif isinstance(ast, List):
        result = GccTuple(*([convert_python_to_gcc_ast(elt) for elt in ast.elts] + [GccConstant(0)]))

    elif isinstance(ast, Subscript):
        value = convert_python_to_gcc_ast(ast.value)
        if isinstance(ast.slice, Slice):
            index = ast.slice.lower.n
            if ast.slice.upper:
                raise Exception("only [N:] syntax is supported")
            # generate only a series of cdr instructions
            result = GccTupleMember(value, index, index+1)
        else:
            # generate cdr + car
            index = ast.slice.value.n
            result = GccTupleMember(value, index, index+2)

    elif isinstance(ast, Call):
        if ast.func.id in GccIntrinsic.variants:
            if len(ast.args) != 1:
                raise Exception("{} expects 1 argument, got {}".format(ast.func.id, len(ast.args)))
            result = GccIntrinsic(ast.func.id, convert_python_to_gcc_ast(ast.args[0]))
        else:
            callee = GccNameReference(ast.func.id)
            result = GccCall(callee,
                             [convert_python_to_gcc_ast(arg) for arg in ast.args])
    else:
        raise Exception("Unsupported Python AST node type {0}".format(ast))
    result.source_location = (ast.lineno, ast.col_offset)
    return result
