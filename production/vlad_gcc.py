import sys
from collections import namedtuple, Counter
from StringIO import StringIO
import logging

sys.path.append('../production')
from gcc_wrapper import GCCInterface, InterpreterException
from gcc_utils import to_int32, deep_marshal, deep_unmarshal
from command_enums import GCC_CMD
from goto import goto


logger = logging.getLogger(__name__)


Frame = namedtuple('Frame', 'parent locals is_dummy') # is_dummy is a list of 0 or 1 elements
Closure = namedtuple('Closure', 'address env')


TAG_JOIN, TAG_RET, TAG_STOP = 0, 1, 2


class VladGCC(GCCInterface):
    def __init__(self, program):
        self.data_stack = []
        self.control_stack = []
        self.env_ptr = None
        self.program = program
        self.pc = 0
        self.build_run_function()
        #self.init_command_map()

    def marshal(self, x):
        if isinstance(x, (int, long)):
            return to_int32(x)
        return x

    def unmarshal(self, x):
        return x

    def call(self, address_or_closure, *args, **kwargs):
        if isinstance(address_or_closure, int):
            addr, env = address_or_closure, Frame(None, [], [])
        else:
            addr, env = address_or_closure
        self.env_ptr = Frame(env, [deep_marshal(self.marshal, arg) for arg in args], [])
        self.pc = addr
        self.control_stack.append((TAG_STOP, 0))

        self.run(kwargs.get('max_ticks'))

        assert len(self.data_stack) == 1
        return deep_unmarshal(self.unmarshal, self.data_stack.pop())

    @staticmethod
    def translate_cmd(pc, cmd, result):
        print>>result, '    # {}'.format(cmd.original_text.strip())
        if cmd.op == GCC_CMD.LDC:
            [arg] = cmd.args
            print>>result, '    self.data_stack.append({})'.format(to_int32(arg))
        elif cmd.op == GCC_CMD.ADD:
            print>>result, '    y = self.pop_int()'
            print>>result, '    x = self.pop_int()'
            print>>result, '    self.data_stack.append(to_int32(x + y))'
        elif cmd.op == GCC_CMD.SUB:
            print>>result, '    y = self.pop_int()'
            print>>result, '    x = self.pop_int()'
            print>>result, '    self.data_stack.append(to_int32(x - y))'
        elif cmd.op == GCC_CMD.MUL:
            print>>result, '    y = self.pop_int()'
            print>>result, '    x = self.pop_int()'
            print>>result, '    self.data_stack.append(to_int32(x * y))'
        elif cmd.op == GCC_CMD.DIV:
            print>>result, '    y = self.pop_int()'
            print>>result, '    x = self.pop_int()'
            print>>result, '    self.data_stack.append(to_int32(x / y))'
        elif cmd.op == GCC_CMD.CGT:
            print>>result, '    y = self.pop_int()'
            print>>result, '    x = self.pop_int()'
            print>>result, '    self.data_stack.append(int(x > y))'
        elif cmd.op == GCC_CMD.CEQ:
            print>>result, '    y = self.pop_int()'
            print>>result, '    x = self.pop_int()'
            print>>result, '    self.data_stack.append(int(x == y))'
        elif cmd.op == GCC_CMD.ATOM:
            print>>result, '    x = self.data_stack.pop()'
            print>>result, '    self.data_stack.append(int(isinstance(x, (int, long))))'
        elif cmd.op == GCC_CMD.CONS:
            print>>result, '    y = self.data_stack.pop()'
            print>>result, '    x = self.data_stack.pop()'
            print>>result, '    self.data_stack.append((x, y))'
        elif cmd.op == GCC_CMD.CAR:
            print>>result, '    x, _ = self.pop_cons()'
            print>>result, '    self.data_stack.append(x)'
        elif cmd.op == GCC_CMD.CDR:
            print>>result, '    _, x = self.pop_cons()'
            print>>result, '    self.data_stack.append(x)'
        elif cmd.op == GCC_CMD.RTN:
            print>>result, '    tag, addr = self.control_stack.pop()'
            print>>result, '    if tag == TAG_STOP:'
            print>>result, '        return'
            # print>>result, '    if tag != TAG_RET:'
            # print>>result, '        raise InterpreterException('
            # print>>result, '            "CONTROL_MISMATCH, expected TAG_RET, got {}".format((tag, addr)))'
            print>>result, '    self.env_ptr = self.control_stack.pop()'
            print>>result, '    self.pc = addr'
            print>>result, '    goto .pc_dispatch'
        elif cmd.op == GCC_CMD.LDF:
            print>>result, '    x = Closure({}, self.env_ptr)'.format(cmd.args[0])
            print>>result, '    self.data_stack.append(x)'
        elif cmd.op == GCC_CMD.AP or cmd.op == GCC_CMD.TAP:
            [arg] = cmd.args
            assert arg >= 0
            print>>result, '    addr, closure_env = self.pop_closure()'
            print>>result, ''
            print>>result, '    offset = len(self.data_stack) - {}'.format(arg)
            print>>result, '    locals = self.data_stack[offset : ]'
            print>>result, '    del self.data_stack[offset : ]'
            print>>result, '    fp = Frame(closure_env, locals, [])'
            if cmd.op == GCC_CMD.AP:
                print>>result, '    self.control_stack.append(self.env_ptr)'
                print>>result, '    self.control_stack.append((TAG_RET, {}))'.format(pc + 1)
            print>>result, '    self.env_ptr = fp'
            print>>result, '    self.pc = addr'
            print>>result, '    goto .pc_dispatch'
        elif cmd.op == GCC_CMD.RAP or cmd.op == GCC_CMD.TRAP:
            [arg] = cmd.args
            assert arg >= 0
            print>>result, '    addr, fp = self.pop_closure()'
            # print>>result, '    if not self.env_ptr.is_dummy:'
            # print>>result, '        raise InterpreterException("FRAME_MISMATCH: frame not dummy {!r}".format(self.env_ptr))'
            # print>>result, '    if len(self.env_ptr.locals) != {}:'.format(arg)
            # print>>result, '        raise InterpreterException("FRAME_MISMATCH: wrong size {{!r}} (need {})".format(self.env_ptr))'.format(arg)
            # print>>result, '    if self.env_ptr != fp:'
            # print>>result, '        raise InterpreterException("FRAME_MISMATCH: wrong frame {!r} (need {!r})".format(self.env_ptr, fp))'
            print>>result, '    offset = len(self.data_stack) - {}'.format(arg)
            print>>result, '    fp.locals[:] = self.data_stack[offset:]'
            print>>result, '    del self.data_stack[offset:]'
            if cmd.op == GCC_CMD.RAP:
                print>>result, '    self.control_stack.append(fp.parent)'
                print>>result, '    self.control_stack.append((TAG_RET, self.pc))'
            print>>result, '    del fp.is_dummy[:] # clear dummy flag'
            print>>result, '    self.pc = addr'
            print>>result, '    goto .pc_dispatch'
        elif cmd.op == GCC_CMD.LD:
            depth, offset = cmd.args
            print>>result, '    fp = self.env_ptr'
            for _ in xrange(depth):
                print>>result, '    fp = fp.parent'
            #print>>result, '    if fp.is_dummy:'
            #print>>result, '        raise InterpreterException("FRAME_MISMATCH: dummy frame {!r}".format(fp))'
            print>>result, '    self.data_stack.append(fp.locals[{}])'.format(offset)
        elif cmd.op == GCC_CMD.ST:
            depth, offset = cmd.args
            print>>result, '    x = self.data_stack.pop()'
            print>>result, '    fp = self.env_ptr'
            for _ in xrange(depth):
                print>>result, '    fp = fp.parent'
            print>>result, '    if fp.is_dummy:'
            print>>result, '        raise InterpreterException("FRAME_MISMATCH: dummy frame {!r}".format(fp))'
            print>>result, '    fp.locals[{}] = x'.format(offset)
        elif cmd.op == GCC_CMD.DUM:
            [arg] = cmd.args
            print>>result, '    fp = Frame(self.env_ptr, [None] * {}, [True])'.format(arg)
            print>>result, '    self.env_ptr = fp'
        elif cmd.op == GCC_CMD.SEL:
            then_label, else_label = cmd.args
            print>>result, '    x = self.pop_int()'
            print>>result, '    self.control_stack.append((TAG_JOIN, {}))'.format(pc + 1)
            print>>result, '    if x:'
            print>>result, '        self.pc = {}'.format(then_label)
            print>>result, '        goto ._instr{}'.format(then_label)
            print>>result, '    else:'
            print>>result, '        self.pc = {}'.format(else_label)
            print>>result, '        goto ._instr{}'.format(else_label)
        elif cmd.op == GCC_CMD.TSEL:
            then_label, else_label = cmd.args
            print>>result, '    x = self.pop_int()'
            print>>result, '    if x:'
            print>>result, '        self.pc = {}'.format(then_label)
            print>>result, '        goto ._instr{}'.format(then_label)
            print>>result, '    else:'
            print>>result, '        self.pc = {}'.format(else_label)
            print>>result, '        goto ._instr{}'.format(else_label)
        elif cmd.op == GCC_CMD.JOIN:
            print>>result, '    tag, addr = self.control_stack.pop()'
            # print>>result, '    if tag is not TAG_JOIN:'
            # print>>result, '        raise InterpreterException("CONTROL_MISMATCH, expected TAG_JOIN, got {}".format(tag))'
            print>>result, '    self.pc = addr'
            print>>result, '    goto .pc_dispatch'
        else:
            assert False, cmd


    @staticmethod
    def build_pc_dispatch(num_cmd, result):
        print>>result, '    label .pc_dispatch'
        print>>result, '    pc = self.pc'
        def rec(i, j, indent):
            if j == i + 1:
                print>>result, '{}goto ._instr{}'.format(indent, i)
                return
            mid = (i + j) // 2
            print>>result, '{}if pc < {}:'.format(indent, mid)
            rec(i, mid, indent + '    ')
            print>>result, '{}else:'.format(indent, mid)
            rec(mid, j, indent + '    ')

        rec(0, num_cmd, '    ')
        print>>result, '    assert False, pc'
        print>>result


    def build_run_function(self):
        result = StringIO()
        # TODO: support max_ticks
        print>>result, '@goto'
        print>>result, 'def run(self, max_ticks):'
        self.build_pc_dispatch(len(self.program), result)
        instr_freq = Counter()
        for i, cmd in enumerate(self.program):
            instr_freq[cmd.op] += 1
            print>>result, '    label ._instr{}'.format(i)
            self.translate_cmd(i, cmd, result)
            print>>result
        logger.info(str(instr_freq))
        exec result.getvalue()
        self.__class__.run = run

    ####

    def pop_int(self):
        x = self.data_stack.pop()
        if type(x) is not int:
            raise InterpreterException('TAG_MISMATCH: got {!r} instead of int'.format(x))
        return x

    def pop_cons(self):
        x = self.data_stack.pop()
        if type(x) is not tuple:
            raise InterpreterException('TAG_MISMATCH: got {!r} instead of tuple'.format(x))
        return x

    def pop_closure(self):
        x = self.data_stack.pop()
        if type(x) is not Closure:
            raise InterpreterException('TAG_MISMATCH: got {!r} instead of closure'.format(x))
        return x



from asm_parser import parse_gcc


def main():
    code = """
        ldc 0
        sel 3 5
        rtn
        ldc 2
        join
        ldc 42
        join
    """
    machine = VladGCC(parse_gcc(code))
    print '------'
    print machine.call(0, [])

if __name__ == '__main__':
    main()
