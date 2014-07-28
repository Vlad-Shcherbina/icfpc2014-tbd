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
        self.assert_code_equals("LDC 3", builder.text)

    def test_add(self):
        c1 = GccConstant(3)
        c2 = GccConstant(4)
        expr = GccAdd(c1, c2)
        blk = GccCodeBlock()
        blk.instructions.append(expr)
        builder = GccTextBuilder()
        blk.emit(builder, None)
        self.assert_code_equals("LDC 3\nLDC 4\nADD\n", builder.text)

    def test_function(self):
        builder = GccTextBuilder()
        body = GccFunction(None, "body", ["x"])
        var_ref = GccNameReference("x")
        expr = GccAdd(var_ref, var_ref)
        body.add_instruction(expr)
        body.emit(builder)
        self.assert_code_equals("""
        ;$func_body$
            LD 0 0
            LD 0 0
            ADD
            RTN
        """, builder.text)

    def test_function_reference(self):
        program = GccProgram()
        body = program.add_function("main", ["x"])
        body.add_instruction(GccNameReference("step"))
        program.add_function("step", ["x"])
        builder = GccTextBuilder()
        program.emit(builder)
        self.assert_code_equals("""
        ;$func_main$
            LDF 2  ; $func_step$
            RTN
        ;$func_step$
            RTN
            """, builder.text)

    def test_function_call(self):
        program = GccProgram()

        main = program.add_function("main", [])
        main.add_instruction(GccCall(GccNameReference("body"), [GccConstant(21)]))
        main.add_instruction(GccConstant(0))

        body = program.add_function("body", ["x"])
        var_ref = GccNameReference("x")
        body.add_instruction(GccAdd(var_ref, var_ref))

        builder = GccTextBuilder()
        program.emit(builder)

        self.assert_code_equals("""
        ;$func_main$
            LDC 21
            LDF 5  ; $func_body$
            AP 1
            LDC 0
            RTN
        ;$func_body$
            LD 0 0
            LD 0 0
            ADD
            RTN
            """, builder.text)

    def test_tail_call(self):
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
            LDC 21
            LDF 3  ; $func_body$
            TAP 1
        ;$func_body$
            LD 0 0
            LD 0 0
            ADD
            RTN
            """, builder.text)

    def test_tail_call_in_condition(self):
        program = GccProgram()

        main = program.add_function("main", [])
        cond = GccConditionalBlock(GccConstant(1))
        main.add_instruction(cond)
        cond.true_branch.instructions.append(GccCall(GccNameReference("body"),
                                                     [GccConstant(21)]))
        cond.false_branch.instructions.append(GccCall(GccNameReference("body"),
                                                      [GccConstant(32)]))

        body = program.add_function("body", ["x"])
        var_ref = GccNameReference("x")
        body.add_instruction(GccAdd(var_ref, var_ref))

        builder = GccTextBuilder()
        program.emit(builder)

        self.assert_code_equals("""
        ;$func_main$
            LDC 1
            TSEL 2 5
            LDC 21
            LDF 8  ; $func_body$
            TAP 1
            LDC 32
            LDF 8  ; $func_body$
            TAP 1
        ;$func_body$
            LD 0 0
            LD 0 0
            ADD
            RTN
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
            LD 0 0
            LDC 0
            CGT
            SEL 7 9
            LDC 1
            ADD
            RTN
            LDC 1
            JOIN
            LDC 0
            JOIN
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
            LD 0 0
            LDC 0
            CGT
            TSEL 4 6
            LDC 1
            RTN
            LDC 0
            RTN
            """, builder.text)

    def test_tuple(self):
        program = GccProgram()
        body = program.add_function("main", ["x"])
        body.add_instruction(GccTuple(GccNameReference("x"), GccConstant(1)))
        builder = GccTextBuilder()
        program.emit(builder)
        self.assert_code_equals("""
        ;$func_main$
            LD 0 0
            LDC 1
            CONS
            RTN
            """, builder.text)

    def test_tuple_member(self):
        program = GccProgram()
        body = program.add_function("main", ["x"])
        body.add_instruction(GccTupleMember(GccNameReference("x"), 1, 3))
        builder = GccTextBuilder()
        program.emit(builder)
        self.assert_code_equals("""
        ;$func_main$
            LD 0 0
            CDR
            CAR
            RTN
            """, builder.text)

    def test_assignment(self):
        program = GccProgram()
        body = program.add_function("main", ["x"])
        body.add_instruction(GccAssignment("y", GccConstant(42)))
        body.add_instruction(GccAssignment("x", GccConstant(239)))
        body.add_instruction(GccTuple(GccNameReference("x"),
                                      GccNameReference("y")))
        builder = GccTextBuilder()
        program.emit(builder)
        self.assert_code_equals("""
        ;$func_main$
            DUM 1
            LDC 0
            LDF 4  ; $func_locals_main$
            TRAP 1
        ;$func_locals_main$
            LDC 42
            ST 0 0
            LDC 239
            ST 1 0
            LD 1 0
            LD 0 0
            CONS
            RTN
            """, builder.text)

    def test_parameter_function_names_conflict(self):
        program = GccProgram()
        body = program.add_function("main", ["main"])
        self.assertRaises(GccSyntaxError, lambda: program.emit(GccTextBuilder()))

    def test_local_function_names_conflict(self):
        program = GccProgram()
        body = program.add_function("main", [])
        body.add_instruction(GccAssignment("main", GccConstant(42)))
        self.assertRaises(GccSyntaxError, lambda: program.emit(GccTextBuilder()))

    def test_nested_functions(self):
        program = GccProgram()
        body = program.add_function("main", ["x"])
        body.add_instruction(GccCall(GccNameReference("nested"), []))
        nested = body.add_nested_function("nested", [])
        nested.add_instruction(GccNameReference("x"))
        builder = GccTextBuilder()
        program.emit(builder)
        self.assert_code_equals("""
        ;$func_main$
            LDF 2  ; $func_main_nested$
            TAP 0
        ;$func_main_nested$
            LD 1 0
            RTN
            """, builder.text)

    def test_nested_function_recursive(self):
        program = GccProgram()
        body = program.add_function("main", ["x"])
        body.add_instruction(GccCall(GccNameReference("nested"), []))
        nested = body.add_nested_function("nested", [])
        nested.add_instruction(GccCall(GccNameReference("nested"), []))
        builder = GccTextBuilder()
        program.emit(builder)
        self.assert_code_equals("""
        ;$func_main$
            LDF 2  ; $func_main_nested$
            TAP 0
        ;$func_main_nested$
            DUM 0
            LDF 2  ; $func_main_nested$
            TRAP 0
            """, builder.text)


if __name__ == '__main__':
    import sys
    import nose
    nose.run_exit(argv=sys.argv + [
        '--verbose', '--with-doctest',
        #'--with-coverage', '--cover-package=production',
        '--logging-level=DEBUG'
        ])
