#GCC implementation
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
        self.ctrl_stack.append({'tag':'TAG_STOP'}) # to be able to stop with RTN without popping an empty stack


    def single_step(self):
        '''
        Executes a single instruction at current %c
        '''
        if self.state == 'error':
            self.__log('step called while in error state')
            return
        cmd = self.program[self.reg_c]
        self.__log('step {} line: {!r}'.format(self.reg_c, cmd.original_text))
        self.__process_cmd(cmd)
        
    def run(self):
        '''
        Runs the program from current position to termination
        Termination can happen due to any error, STOP command or popping TAG_STOP during RTN
        '''
        self.state = 'executing'
        while not self.terminal_state:
            self.__log(str(self))
            self.single_step()
        self.__log(str(self))

    # GCCInterface methods
    
    def marshall_int(self, i):
        return {'tag': 'int', 'value': i}
    
    def marshall_cons(self, car, cdr):
        return {'tag': 'cons', 'value': (car, cdr)}
    
    def initialize(self, world_state, undocumented):
        '''world_state must be an opaque handle constructed via marshall_* methods.
        returns (ai_state, step_function)'''
    
    def step(self, ai_state, world_state):
        '''returns ai_state, move. Move is an already decoded integer.'''
        
    #Following methods are intended for internal use only
        
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
    code = '''
  DUM  2        ; 2 top-level declarations
  LDF  go       ; declare function go
  LDF  to       ; declare function to
  LDF  main     ; main function
  RAP  2        ; load declarations into environment and run main
  RTN           ; final return
main:
  LDC  1
  LD   0 0      ; var go
  AP   1        ; call go(1)
  RTN
to:
  LD   0 0      ; var n
  LDC  1
  SUB
  LD   1 0      ; var go
  AP   1        ; call go(n-1)
  RTN
go:
  LD   0 0      ; var n
  LDC  1
  ADD
  LD   1 1      ; var to
  AP   1        ; call to(n+1)
  RTN'''
    from asm_parser import parse_gcc
    program = parse_gcc(code, '<stdin>')
    gcc = VorberGCC(program, verbose=True)
    gcc.run()
    
if __name__ == '__main__':
    main()