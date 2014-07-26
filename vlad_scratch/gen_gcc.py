import sys

sys.path.append('../yole_scratch')
from gcc_ast import *


def main():
    program = GccProgram()

    program.add_standard_main_function()

    init = program.add_function("init", ["world"])
    init.add_instruction(GccInline("""
        LDC  42
        LD   0 1      ; var step
        CONS
    """))

    body = program.add_function("step", ["cur_state", "world"])
    body.add_instruction(GccConstant(42))  # state
    body.add_instruction(GccConstant(1))  # direction
    body.add_instruction(GccInline("CONS"))

    builder = GccTextBuilder()
    program.emit(builder)

    print builder.text.upper()



if __name__ == '__main__':
    main()
