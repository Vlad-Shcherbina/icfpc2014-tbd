from collections import namedtuple

from gcc_wrapper import GCCInterface
from command_enums import GCC_CMD

import logging
log = logging.getLogger(__name__)


Frame = namedtuple('Frame', 'parent slots is_dummy') # is_dummy is a list of 0 or 1 elements
Closure = namedtuple('Closure', 'address env')


class InterpreterException(Exception):
    pass


def to_int32(x):
    return (x & 0xFFFFFFFF) - ((x & 0x80000000) << 1)


TAG_JOIN, TAG_RET, TAG_STOP = 0, 1, 2 


class Interpreter(GCCInterface):
    def __init__(self, program):
        self.data_stack = []
        self.control_stack = []
        self.env_ptr
        self.program = program
        self.pc = 0
        
    def marshall_int(self, i):
        return to_int32(i)
    
    def marshall_cons(self, car, cdr):
        return (car, cdr)
    
    
    def call(self, address_or_closure, *args):
        if isinstance(address_or_closure, (int, long)):
            self.pc = address_or_closure
            self.env_ptr = Frame(None, args, [])
        else:
            self.pc, self.env_ptr = address_or_closure 
        self.control_stack.append((TAG_STOP, 0))
        self.run()
        # don't allow weirdness
        assert len(self.data_stack) == 1
        return self.data_stack.pop()
    
    
    def run(self):
        for cycles in xrange(0, 1048570): # lift the restriction for the initialization phase?
            cmd = self.program[self.pc]
            self.pc += 1
            log.debug(cmd)
            if self.command_map[cmd.op](cmd.args):
                break
        else:
            raise InterpreterException('OUT OF CYCLES OMG')
        log.info('done in {} cycles'.format(cycles))
        
    
    ####
    
    def pop_int(self):
        x = self.data_stack.pop()
        if not isinstance(x, (int, long)):
            raise InterpreterException('TAG_MISMATCH: got {!r} instead of int'.format(x))
        return x
            
    def pop_cons(self):
        x = self.data_stack.pop()
        if not type(x) is not tuple:
            raise InterpreterException('TAG_MISMATCH: got {!r} instead of tuple'.format(x))
        return x
    
    def pop_closure(self):
        x = self.data_stack.pop()
        if not type(x) is not Closure:
            raise InterpreterException('TAG_MISMATCH: got {!r} instead of closure'.format(x))
        return x
    
    # instructions
    
    def eval_LDC(self, args):
        self.data_stack.append(args[0])
        
    
    def eval_LD(self, args):
        depth, offset = args
        fp = self.env_ptr
        for _ in xrange(depth):
            fp = fp.parent
        if fp.is_dummy:
            raise InterpreterException('FRAME_MISMATCH: dummy frame {!r}'.format(fp))
        self.data_stack.append(fp.slots[offset])
        

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
        self.data_stack.append(x == y)

    
    def eval_CGT(self, args):
        y = self.pop_int()
        x = self.pop_int()
        self.data_stack.append(x > y)


    def eval_CGTE(self, args):
        y = self.pop_int()
        x = self.pop_int()
        self.data_stack.append(x >= y)
        
        
    def eval_ATOM(self, args):
        x = self.data_stack.pop()
        self.data_stack.append(isinstance(x, (int, long)))


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
        self.control_stack.append((TAG_JOIN, self.c))
        self.c = args[x != 0]


    def eval_JOIN(self, args):
        tag, addr = self.control_stack.pop()
        if tag is not TAG_JOIN:
            raise InterpreterException('CONTROL_MISMATCH, expected TAG_JOIN, got {}'.format(tag))
        self.c = addr


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
        
        self.control_stack.push(self.env_ptr)
        self.control_stack.push((TAG_RET, self.c))
        self.env_ptr = fp
        self.c = addr


    def eval_RTN(self, args):
        tag, addr = self.control_stack.pop()
        if tag == TAG_STOP:
            return True
        if tag != TAG_RET:
            raise InterpreterException('CONTROL_MISMATCH, expected TAG_RET, got {}'.format((tag, addr)))
        self.env_ptr = self.control_stack.pop()
        self.c = addr


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
        fp.locals = self.data_stack[offset : ]
        del self.data_stack[offset : ]
        
        self.control_stack.push(fp.parent)
        self.control_stack.push((TAG_RET, self.c))
        del fp.is_dummy[:] # clear dummy flag
        #self.env_ptr = fp # unnecessary lol
        self.c = addr
        

    def eval_STOP(self, args):
        return True


    def eval_TSEL(self, args):
        x = self.pop_int()
        self.c = args[x != 0]


    def eval_TAP(self, args):
        addr, closure_env = self.pop_closure()
        
        assert args[0] >= 0
        offset = len(self.data_stack) - args[0]
        locals = self.data_stack[offset : ]
        del self.data_stack[offset : ]
        
        fp = Frame(closure_env, locals, [])
        
        self.env_ptr = fp
        self.c = addr


    def eval_TRAP(self, args):
        addr, fp = self.pop_closure()

        if not self.env_ptr.is_dummy:
            raise InterpreterException('FRAME_MISMATCH: frame not dummy {!r}'.format(self.env_ptr))
        if len(self.env_ptr.locals) != args[0]:
            raise InterpreterException('FRAME_MISMATCH: wrong size {!r} (need {!r})'.format(self.env_ptr, args[0]))
        if self.env_ptr != fp:
            raise InterpreterException('FRAME_MISMATCH: wrong frame {!r} (need {!r})'.format(self.env_ptr, fp))
        
        # create locals because eval_DUM didn't allocate them.
        assert args[0] >= 0
        offset = len(self.data_stack) - args[0]
        fp.locals = self.data_stack[offset : ]
        del self.data_stack[offset : ]
        
        del fp.is_dummy[:] # clear dummy flag
        #self.env_ptr = fp # unnecessary lol
        self.c = addr


    def eval_ST(self, args):
        x = self.data_stack.pop()
        depth, offset = args
        fp = self.env_ptr
        for _ in xrange(depth):
            fp = fp.parent
        if fp.is_dummy:
            raise InterpreterException('FRAME_MISMATCH: dummy frame {!r}'.format(fp))
        fp.slots[offset] = x
        

    def eval_DBUG(self, args):
        x = self.data_stack.pop()
        print 'DEBUG: {!r}'.format(x)
        
    
    def eval_BRK(self, args):
        pass


    command_map = {
            GCC_CMD.LDC : eval_LDC,
            GCC_CMD.LD  : eval_LD,
            GCC_CMD.ADD : eval_ADD,
            GCC_CMD.SUB : eval_SUB,
            GCC_CMD.MUL : eval_MUL,
            GCC_CMD.DIV : eval_DIV,
            GCC_CMD.CEQ : eval_CEQ,
            GCC_CMD.CGT : eval_CGT,
            GCC_CMD.CGTE: eval_CGTE,
            GCC_CMD.ATOM: eval_ATOM,
            GCC_CMD.CONS: eval_CONS,
            GCC_CMD.CAR : eval_CAR,
            GCC_CMD.CDR : eval_MY_OTHER_CAR,
            GCC_CMD.SEL : eval_SEL,
            GCC_CMD.JOIN: eval_JOIN,
            GCC_CMD.LDF : eval_LDF,
            GCC_CMD.AP  : eval_AP,
            GCC_CMD.RTN : eval_RTN,
            GCC_CMD.DUM : eval_DUM,
            GCC_CMD.RAP : eval_RAP,
            GCC_CMD.STOP: eval_STOP,
            GCC_CMD.TSEL: eval_TSEL,
            GCC_CMD.TAP : eval_TAP,
            GCC_CMD.TRAP: eval_TRAP,
            GCC_CMD.ST  : eval_ST,
            GCC_CMD.DBUG: eval_DBUG,
            GCC_CMD.BRK : eval_BRK,
    }
            
