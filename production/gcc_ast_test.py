import unittest
import logging

from gcc_ast import *

logger = logging.getLogger(__name__)


class GccASTTest(unittest.TestCase):
    def assert_code_equals(self, expected, actual):
        def drop_ws(code):
            result = []
            for line in code.splitlines():
                #line, _, _ = line.partition(';')
                # ignore labels within functions,
                # they are implementation details
                if line.startswith(';$label_'):
                    continue
                line = line.strip()
                if line:
                    result.append(line)
            return result
        logging.info('Expected:\n{}'.format(expected))
        logging.info('Actual:\n{}'.format(actual))
        self.assertEquals(drop_ws(expected), drop_ws(actual))

    def test_constant(self):
        blk = GccCodeBlock()
        blk.instructions.append(GccConstant(3))
        builder = GccTextBuilder()
        blk.emit(builder, None)
        self.assert_code_equals("ldc 3", builder.text)

    def test_add(self):
        c1 = GccConstant(3)
        c2 = GccConstant(4)
        expr = GccAdd(c1, c2)
        blk = GccCodeBlock()
        blk.instructions.append(expr)
        builder = GccTextBuilder()
        blk.emit(builder, None)
        self.assert_code_equals("ldc 3\nldc 4\nadd\n", builder.text)

    def test_function(self):
        builder = GccTextBuilder()
        body = GccFunction(None, "body", ["x"])
        var_ref = GccNameReference("x")
        expr = GccAdd(var_ref, var_ref)
        body.add_instruction(expr)
        body.emit(builder)
        self.assert_code_equals("ld 0 0\nld 0 0\nadd\nrtn\n", builder.text)

    def test_function_reference(self):
        program = GccProgram()
        body = program.add_function("main", ["x"])
        body.add_instruction(GccNameReference("step"))
        program.add_function("step", ["x"])
        builder = GccTextBuilder()
        program.emit(builder)
        self.assert_code_equals("""
        ;$func_main$
            ldf 2  ; $func_step$
            rtn
        ;$func_step$
            rtn
            """, builder.text)


    def test_function_call(self):
        program = GccProgram()

        main = program.add_function("main", [])
        main.add_instruction(GccCall(GccNameReference("body"), [GccConstant(21)]))

        body = program.add_function("body", ["x"])
        var_ref = GccNameReference("x")
        body.add_instruction(GccAdd(var_ref, var_ref))

        builder = GccTextBuilder()
        program.emit(builder)

        self.assert_code_equals("""
        ;$func_main$
            ldc 21
            ldf 4  ; $func_body$
            ap 1
            rtn
        ;$func_body$
            ld 0 0
            ld 0 0
            add
            rtn
            """, builder.text)

    def test_conditional_expression(self):
        program = GccProgram()
        body = program.add_function("main", ["x"])
        var_ref = GccNameReference("x")
        conditional_block = GccConditionalBlock(GccGt(var_ref, GccConstant(0)))
        conditional_block.true_branch.instructions.append(GccConstant(1))
        conditional_block.false_branch.instructions.append(GccConstant(0))
        body.add_instruction(GccAdd(conditional_block, GccConstant(1)))
        builder = GccTextBuilder()
        program.emit(builder)
        self.assert_code_equals("""
        ;$func_main$
            ld 0 0
            ldc 0
            cgt
            sel 7 9
            ldc 1
            add
            rtn
            ldc 1
            join
            ldc 0
            join
            """, builder.text)

    def test_tail_conditional_expression(self):
        program = GccProgram()
        body = program.add_function("main", ["x"])
        var_ref = GccNameReference("x")
        conditional_block = GccConditionalBlock(GccGt(var_ref, GccConstant(0)))
        conditional_block.true_branch.instructions.append(GccConstant(1))
        conditional_block.false_branch.instructions.append(GccConstant(0))
        body.add_instruction(conditional_block)
        builder = GccTextBuilder()
        program.emit(builder)
        self.assert_code_equals("""
        ;$func_main$
            ld 0 0
            ldc 0
            cgt
            tsel 4 6
            ldc 1
            rtn
            ldc 0
            rtn
            """, builder.text)

    def test_tuple(self):
        program = GccProgram()
        body = program.add_function("main", ["x"])
        body.add_instruction(GccTuple(GccNameReference("x"), GccConstant(1)))
        builder = GccTextBuilder()
        program.emit(builder)
        self.assert_code_equals("""
        ;$func_main$
            ld 0 0
            ldc 1
            cons
            rtn
            """, builder.text)

    def test_tuple_member(self):
        program = GccProgram()
        body = program.add_function("main", ["x"])
        body.add_instruction(GccTupleMember(GccNameReference("x"), 1, 3))
        builder = GccTextBuilder()
        program.emit(builder)
        self.assert_code_equals("""
        ;$func_main$
            ld 0 0
            cdr
            car
            rtn
            """, builder.text)


if __name__ == '__main__':
    import sys
    import nose
    nose.run_exit(argv=sys.argv + [
        '--verbose', '--with-doctest',
        #'--with-coverage', '--cover-package=production',
        '--logging-level=DEBUG'
        ])
