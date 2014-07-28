from collections import namedtuple

from gcc_wrapper import GCCInterface, InterpreterException
from command_enums import GCC_CMD
from gcc_utils import to_int32, deep_marshal, deep_unmarshal

import logging
log = logging.getLogger(__name__)


Frame = namedtuple('Frame', 'parent locals is_dummy') # is_dummy is a list of 0 or 1 elements
Closure = namedtuple('Closure', 'address env')



TAG_JOIN, TAG_RET, TAG_STOP = 0, 1, 2 


class FjGCC(GCCInterface):
    def __init__(self, program):
        self.data_stack = []
        self.control_stack = []
        self.env_ptr = None
        self.program = program
        self.pc = 0
        self.init_command_map()

        
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
        # don't allow weirdness
        assert len(self.data_stack) == 1
        return deep_unmarshal(self.unmarshal, self.data_stack.pop())
    
    
    def step(self):
        cmd = self.program[self.pc]
#        print self.data_stack
#        print self.env_ptr
#        print self.pc, cmd.op, cmd.args
        self.pc += 1
        return self.command_map[cmd.op](cmd.args)
            
    
    def run(self, max_ticks=None):
        for cycles in xrange(0, max_ticks or 1048570):
            if self.step():
                break
        else:
            raise InterpreterException('OUT OF CYCLES OMG')
        log.info('done in {} cycles'.format(cycles))
        
    
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
    
    # instructions
    
    def eval_LDC(self, args):
        self.data_stack.append(to_int32(args[0]))
        
    
    def eval_LD(self, args):
        depth, offset = args
        fp = self.env_ptr
        for _ in xrange(depth):
            fp = fp.parent
        if fp.is_dummy:
            raise InterpreterException('FRAME_MISMATCH: dummy frame {!r}'.format(fp))
        self.data_stack.append(fp.locals[offset])
        

    def eval_ADD(self, args):
        y = self.pop_int()
        x = self.pop_int()
        self.data_stack.append(to_int32(x + y))
        

    def eval_SUB(self, args):
        y = self.pop_int()
        x = self.pop_int()
        self.data_stack.append(to_int32(x - y))

    
    def eval_MUL(self, args):
        y = self.pop_int()
        x = self.pop_int()
        self.data_stack.append(to_int32(x * y))
        
    
    def eval_DIV(self, args):
        y = self.pop_int()
        x = self.pop_int()
        self.data_stack.append(to_int32(x / y))


    def eval_CEQ(self, args):
        y = self.pop_int()
        x = self.pop_int()
        self.data_stack.append(int(x == y))

    
    def eval_CGT(self, args):
        y = self.pop_int()
        x = self.pop_int()
        self.data_stack.append(int(x > y))


    def eval_CGTE(self, args):
        y = self.pop_int()
        x = self.pop_int()
        self.data_stack.append(int(x >= y))
        
        
    def eval_ATOM(self, args):
        x = self.data_stack.pop()
        self.data_stack.append(int(isinstance(x, (int, long))))


    def eval_CONS(self, args):
        y = self.data_stack.pop()
        x = self.data_stack.pop()
        self.data_stack.append((x, y))


    def eval_CAR(self, args):
        x, _ = self.pop_cons()
        self.data_stack.append(x)


    def eval_MY_OTHER_CAR(self, args):
        _, y = self.pop_cons()
        self.data_stack.append(y)


    def eval_SEL(self, args):
        x = self.pop_int()
        self.control_stack.append((TAG_JOIN, self.pc))
        self.pc = args[x == 0]


    def eval_JOIN(self, args):
        tag, addr = self.control_stack.pop()
        if tag is not TAG_JOIN:
            raise InterpreterException('CONTROL_MISMATCH, expected TAG_JOIN, got {}'.format(tag))
        self.pc = addr


    def eval_LDF(self, args):
        x = Closure(args[0], self.env_ptr)
        self.data_stack.append(x)


    def eval_AP(self, args):
        addr, closure_env = self.pop_closure()
        
        assert args[0] >= 0
        offset = len(self.data_stack) - args[0]
        locals = self.data_stack[offset : ]
        del self.data_stack[offset : ]
        
        fp = Frame(closure_env, locals, [])
        
        self.control_stack.append(self.env_ptr)
        self.control_stack.append((TAG_RET, self.pc))
        self.env_ptr = fp
        self.pc = addr


    def eval_RTN(self, args):
        tag, addr = self.control_stack.pop()
        if tag == TAG_STOP:
            return True
        if tag != TAG_RET:
            raise InterpreterException('CONTROL_MISMATCH, expected TAG_RET, got {}'.format((tag, addr)))
        self.env_ptr = self.control_stack.pop()
        self.pc = addr


    def eval_DUM(self, args):
        fp = Frame(self.env_ptr, [None] * args[0], [True]) 
        self.env_ptr = fp


    def eval_RAP(self, args):
        addr, fp = self.pop_closure()

        if not self.env_ptr.is_dummy:
            raise InterpreterException('FRAME_MISMATCH: frame not dummy {!r}'.format(self.env_ptr))
        if len(self.env_ptr.locals) != args[0]:
            raise InterpreterException('FRAME_MISMATCH: wrong size {!r} (need {!r})'.format(self.env_ptr, args[0]))
        if self.env_ptr != fp:
            raise InterpreterException('FRAME_MISMATCH: wrong frame {!r} (need {!r})'.format(self.env_ptr, fp))
        
        assert args[0] >= 0
        offset = len(self.data_stack) - args[0]
        fp.locals[:] = self.data_stack[offset:]
        del self.data_stack[offset:]
        
        self.control_stack.append(fp.parent)
        self.control_stack.append((TAG_RET, self.pc))
        del fp.is_dummy[:] # clear dummy flag
        #self.env_ptr = fp # unnecessary lol
        self.pc = addr
        

    def eval_STOP(self, args):
        return True


    def eval_TSEL(self, args):
        x = self.pop_int()
        self.pc = args[x == 0]


    def eval_TAP(self, args):
        addr, closure_env = self.pop_closure()
        
        assert args[0] >= 0
        offset = len(self.data_stack) - args[0]
        locals = self.data_stack[offset : ]
        del self.data_stack[offset : ]
        
        fp = Frame(closure_env, locals, [])
        
        self.env_ptr = fp
        self.pc = addr


    def eval_TRAP(self, args):
        addr, fp = self.pop_closure()

        if not self.env_ptr.is_dummy:
            raise InterpreterException('FRAME_MISMATCH: frame not dummy {!r}'.format(self.env_ptr))
        if len(self.env_ptr.locals) != args[0]:
            raise InterpreterException('FRAME_MISMATCH: wrong size {!r} (need {!r})'.format(self.env_ptr, args[0]))
        if self.env_ptr != fp:
            raise InterpreterException('FRAME_MISMATCH: wrong frame {!r} (need {!r})'.format(self.env_ptr, fp))
        
        assert args[0] >= 0
        offset = len(self.data_stack) - args[0]
        fp.locals[:] = self.data_stack[offset:]
        del self.data_stack[offset:]
        
        del fp.is_dummy[:] # clear dummy flag
        #self.env_ptr = fp # unnecessary lol
        self.pc = addr


    def eval_ST(self, args):
        x = self.data_stack.pop()
        depth, offset = args
        fp = self.env_ptr
        for _ in xrange(depth):
            fp = fp.parent
        if fp.is_dummy:
            raise InterpreterException('FRAME_MISMATCH: dummy frame {!r}'.format(fp))
        fp.locals[offset] = x
        

    def eval_DBUG(self, args):
        x = self.data_stack.pop()
        print 'DEBUG: {!r}'.format(x)
        
    
    def eval_BRK(self, args):
        pass


    def init_command_map(self):
        self.command_map = {
                GCC_CMD.LDC : self.eval_LDC,
                GCC_CMD.LD  : self.eval_LD,
                GCC_CMD.ADD : self.eval_ADD,
                GCC_CMD.SUB : self.eval_SUB,
                GCC_CMD.MUL : self.eval_MUL,
                GCC_CMD.DIV : self.eval_DIV,
                GCC_CMD.CEQ : self.eval_CEQ,
                GCC_CMD.CGT : self.eval_CGT,
                GCC_CMD.CGTE: self.eval_CGTE,
                GCC_CMD.ATOM: self.eval_ATOM,
                GCC_CMD.CONS: self.eval_CONS,
                GCC_CMD.CAR : self.eval_CAR,
                GCC_CMD.CDR : self.eval_MY_OTHER_CAR,
                GCC_CMD.SEL : self.eval_SEL,
                GCC_CMD.JOIN: self.eval_JOIN,
                GCC_CMD.LDF : self.eval_LDF,
                GCC_CMD.AP  : self.eval_AP,
                GCC_CMD.RTN : self.eval_RTN,
                GCC_CMD.DUM : self.eval_DUM,
                GCC_CMD.RAP : self.eval_RAP,
                GCC_CMD.STOP: self.eval_STOP,
                GCC_CMD.TSEL: self.eval_TSEL,
                GCC_CMD.TAP : self.eval_TAP,
                GCC_CMD.TRAP: self.eval_TRAP,
                GCC_CMD.ST  : self.eval_ST,
                GCC_CMD.DBUG: self.eval_DBUG,
                GCC_CMD.BRK : self.eval_BRK,
        }
            
