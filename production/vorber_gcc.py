#GCC implementation
import sys
from command_enums import GCC_CMD
from gcc_wrapper import GCCInterface

class VorberGCC(GCCInterface):
    def __init__(self, program, verbose=False):
        '''Specifying verbose=True enables diagnostics spam via prints''' # dude, use logging.
        self.verbose = verbose
        self.program = program
        self.reset()
        self.state = 'loaded'
        self.__log(str(self))

    def __str__(self):
        regs = 'Regs: c:{0} s:{1} d:{2} e:{3}'.format(self.reg_c, self.reg_s, self.reg_d, self.reg_e)
        ds = 'Data: ' + str(self.data_stack)
        cs = 'Ctrl: ' + str(self.ctrl_stack)
        es = 'Env:  ' + str(self.env_stack)
        result = '\n'.join((regs, ds, cs, es, 'state: ' + self.state))
        return result

    def reset(self):
        '''
        Resets itself to initial state
        '''
        self.reg_c = 0
        self.reg_s = 0
        self.reg_d = 0
        self.reg_e = -1 #because 0 already points at valid place in env_stack, which is empty now
        self.data_stack = []
        self.ctrl_stack = []
        self.env_stack = []
        self.terminal_state = False
        self.state = 'empty'
        # this should go to "run", I guess?


    def single_step(self):
        '''
        Executes a single instruction at current %c
        '''
        self.__log('single_step: enter')
        if self.state == 'error':
            self.__log('step called while in error state')
            return
        cmd = self.program[self.reg_c]
        self.__log('step {} line: {!r}'.format(self.reg_c, cmd.original_text))
        self.__process_cmd(cmd)
        self.__log('single_step: exit')

    def run(self):
        '''
        Runs the program from current position to termination
        Termination can happen due to any error, STOP command or popping TAG_STOP during RTN
        '''
        self.__log('run: enter')
        self.state = 'executing'
        while not self.terminal_state:
            self.__log(str(self))
            self.single_step()
        self.__log(str(self))
        self.__log('run: exit')

    # GCCInterface methods

    def marshall_int(self, i):
        return {'tag': 'int', 'value': i}

    def marshall_cons(self, car, cdr):
        return {'tag': 'cons', 'value': (car, cdr)}

    def call(self, address_or_closure, *args):
        'Call a function. Put args on the data stack, return contents of the data stack after the function returns'
        # Implement the stuff below, OK?
        'reset all stacks' #vorber: gcc state persists between calls, unless explicitly modified from outside
        'put args on the data stack'
        #[00:51] <jdreske> the lambda man cpu simulator always starts with empty data stack, but usually we will have two elements on it, world and undefined, right?
        #[00:52] <@dcoutts> jdreske: no, function args come in via the environment, not the stack
        #
        #so args go on env stack, not data
        self.terminal_state = False
        self.__log('call: ' + str(self) + '::'+str(address_or_closure))
        fp = {'frame_tag':'FRAME_NO_TAG', 'parent':-1, 'values':[arg for arg in args], 'size':len(args)}
        self.ctrl_stack.append({'tag':'TAG_STOP'})
        if isinstance(address_or_closure, int):
            self.env_stack.append(fp)
            self.reg_e = len(self.env_stack)-1
            self.reg_c = address_or_closure
        else:
            # it's a closure
            'set self.reg_c and self.reg_e from the closure'
            self.reg_c = address_or_closure['value'][0]
            self.reg_e = address_or_closure['value'][1]
            while len(self.env_stack) < self.reg_e+1:
                self.env_stack.append({})
            self.env_stack = self.env_stack[:self.reg_e+1]
            self.env_stack[self.reg_e] = fp
        self.run()
        'return everything on the data stack'
        #not everything, as per spec we always return a 'pair' i.e. CONS
        ret = self.data_stack.pop()
        if (ret['tag'] != 'cons'):
            self.__error('return value is not CONS')
            return (0,0)
        tret = self.__cons_to_tuple(ret)
        self.__log('call: returning' + str(tret))

        return tret



    #Following methods are intended for internal use only
    def __cons_to_tuple(self, cons):
        t = map(lambda v: v['value'] if v['tag'] == 'int' else v, cons['value'])
        return (t[0],t[1])
        
            
    def __log(self, s):
        if self.verbose:
            print s



    def __error(self, e):
        self.__log("ERROR: " + str(e))
        self.state = 'error'
        self.terminal_state = True

    def __process_arithmetic_cmd(self, op):
        y = self.data_stack.pop()
        x = self.data_stack.pop()
        self.__match_tag(x, 'int')
        self.__match_tag(y, 'int')
        if self.terminal_state:
            return
        z = op(x['value'],y['value'])
        self.data_stack.append({'tag':'int', 'value':z})
        self.reg_c += 1

    def __process_extract_cons(self, idx):
        x = self.data_stack.pop()
        self.__match_tag(x,'cons')
        if self.terminal_state:
            return
        y = x['value'][idx]
        self.data_stack.append({'tag':'int', 'value':y})
        self.reg_c += 1

    def __match_tag(self, x,tag):
        if x['tag'] != tag:
            self.__error('TAG_MISMATCH')

    def __process_cmd(self, cmd):
        op = cmd.op
        if op == GCC_CMD.LDC:
            self.data_stack.append({'tag': 'int', 'value': cmd.args[0]})
            self.reg_c += 1
        elif op == GCC_CMD.LD:
            fp = self.env_stack[-1]
            n, i = cmd.args
            while n > 0:
                fp = self.env_stack[fp['parent']]
                n -= 1
            if fp['frame_tag'] == 'TAG_DUM':
                self.__error('FRAME_MISMATCH')
                return
            v = fp['values'][i]
            self.data_stack.append(v)
            self.reg_c += 1
        elif op == GCC_CMD.ADD:
            self.__process_arithmetic_cmd(lambda a,b:a+b)
        elif op == GCC_CMD.SUB:
            self.__process_arithmetic_cmd(lambda a,b:a-b)
        elif op == GCC_CMD.MUL:
            self.__process_arithmetic_cmd(lambda a,b:a*b)
        elif op == GCC_CMD.DIV:
            self.__process_arithmetic_cmd(lambda a,b:a/b)
        elif op == GCC_CMD.CEQ:
            self.__process_arithmetic_cmd(lambda a,b: 1 if a==b else 0)
        elif op == GCC_CMD.CGT:
            self.__process_arithmetic_cmd(lambda a,b: 1 if a>b else 0)
        elif op == GCC_CMD.CGTE:
            self.__process_arithmetic_cmd(lambda a,b: 1 if a>=b else 0)
        elif op == GCC_CMD.ATOM:
            x = self.data_stack.pop()
            self.data_stack.append({'tag':'int', 'value': 1 if x['tag'] == 'int' else 0})
            self.reg_c += 1
        elif op == GCC_CMD.CONS:
            y = self.data_stack.pop()
            x = self.data_stack.pop()
            self.data_stack.append({'tag':'cons', 'value':(x,y)})
            self.reg_c += 1
        elif op == GCC_CMD.CAR:
            self.__process_extract_cons(0)
        elif op == GCC_CMD.CDR:
            self.__process_extract_cons(0)
        elif op == GCC_CMD.SEL:
            x = self.data_stack.pop()
            self.__match_tag(x, 'int')
            if self.terminal_state:
                return
            self.ctrl_stack.append({'tag':'join', 'value':self.reg_c+1})
            self.reg_c = cmd.args[x == 0]
        elif op == GCC_CMD.JOIN:
            x = self.ctrl_stack.pop()
            if x['tag'] != 'join':
                self.__error('CONTROL_MISMATCH')
                return
            self.reg_c = x
        elif op == GCC_CMD.LDF:
            closure = (cmd.args[0], self.reg_e)
            self.data_stack.append({'tag':'closure','value':closure})
            self.reg_c += 1
        elif op == GCC_CMD.AP:
            x = self.data_stack.pop()
            self.__match_tag(x,'closure')
            if self.terminal_state:
                return
            f = x['value'][0]
            e = x['value'][1]
            fp = {'frame_tag':'FRAME_NO_TAG', 'parent':e, 'values':[{} for i in range(cmd.args[0])], 'size':cmd.args[0]}
            i = cmd.args[0]-1
            while i != -1:
                y = self.data_stack.pop()
                fp['values'][i] = y
                i -= 1
            self.ctrl_stack.append({'tag':'WTFNOTAG!11AP', 'value':self.reg_e})
            self.ctrl_stack.append({'tag':'TAG_RET', 'value':self.reg_c+1})
            self.env_stack.append(fp)
            self.reg_e += 1 #len(self.env_stack) - 1
            self.reg_c = f
        elif op == GCC_CMD.RTN:
            x = self.ctrl_stack.pop()
            if x['tag'] == 'TAG_STOP':
                self.terminal_state = True
                self.state='finished'
                return
            if x['tag'] != 'TAG_RET':
                self.__error('CONTROL_MISMATCH')
            y = self.ctrl_stack.pop()
            self.reg_e = y['value']
            #environments only have link to parent, not to children
            #therefore as soon as we get to frame y all its children are lost?
            self.env_stack = self.env_stack[:y['value']+1] #maybe popping a few times would be faster?
            self.reg_c = x['value'];
        elif op == GCC_CMD.DUM:
            fp = {'frame_tag':'TAG_DUM','parent':self.reg_e, 'values':[{} for i in range(cmd.args[0])], 'size': cmd.args[0]}
            self.env_stack.append(fp)
            self.reg_e += 1
            self.reg_c += 1
        elif op == GCC_CMD.RAP:
            x = self.data_stack.pop()
            self.__match_tag(x,'closure')
            if self.terminal_state:
                return

            f = x['value'][0]
            fp = x['value'][1]

            ef = self.env_stack[self.reg_e]
            if ef['frame_tag'] != 'TAG_DUM' or ef['size'] != cmd.args[0] or self.reg_e != fp:
                self.__error('FRAME_MISMATCH')
            i = cmd.args[0] - 1
            while i != -1:
                y = self.data_stack.pop()
                ef['values'][i] = y
                i -= 1
            ep = ef['parent']
            self.ctrl_stack.append({'tag':'WTFNOTAG!11RAP', 'value':ep})
            self.ctrl_stack.append({'tag':'TAG_RET', 'value':self.reg_c+1})
            ef['frame_tag'] = 'FRAME_TAG_NORMAL'
            #self.reg_e = fp #[23:43] <@dcoutts> vorber: it's excessive
            self.reg_c = f
        elif op == GCC_CMD.STOP:
            self.terminal_state=True
        else:
            self.__error('UNKNOWN CMD: {}'.format(cmd))

def main():
    #filename = '../data/lms/goto.gcc'
    filename = 'exampleai.gcc'
    code = open(filename).read()
    from asm_parser import parse_gcc
    program = parse_gcc(code, source=filename)
    gcc = VorberGCC(program, verbose=True)
    #gcc.run()
    gcc.call(0, (0,0), (0,0))

if __name__ == '__main__':
    main()
