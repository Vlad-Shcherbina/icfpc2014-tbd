import sys

sys.path.append('../production')
import game
sys.path.append('../yole_scratch')
from gcc_ast import *


def main():
    program = GccProgram()

    program.add_standard_main_function()

    init = program.add_function("init", ["world"])
    init.add_instruction(GccInline("""
        LDC  42
        LD   0 1      ; var step
        CONS  ; pair (42, step)
    """))

    nth = program.add_function("nth", ["idx", "list"])
    idx = GccNameReference("idx")
    list = GccNameReference("list")
    conditional_block = GccConditionalBlock(GccEq(idx, GccConstant(0)))
    conditional_block.true_branch.instructions.append(
        GccTupleMember(list, 0, 2))
    conditional_block.false_branch.instructions.append(
        GccCall(GccNameReference("nth"),
            [GccSub(idx, GccConstant(1)),
             GccTupleMember(list, 1, 2)]))
    nth.add_instruction(conditional_block)


    body = program.add_function("step", ["cur_state", "world"])
    #body.add_instruction(GccConstant(42))  # state
    body.add_instruction(GccTupleMember(GccNameReference("world"), 0, 4))
    body.add_instruction(GccConstant(1))  # direction
    body.add_instruction(GccInline("CONS"))

    builder = GccTextBuilder()
    program.emit(builder)

    text = builder.text.upper()
    print text

    with open('../data/lms/crap.gcc', 'w') as fout:
        print>>fout, '; generated by vlad_scratch/gen_gcc.py'
        print>>fout, text



if __name__ == '__main__':
    main()
