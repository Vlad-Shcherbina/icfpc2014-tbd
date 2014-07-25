#GCC implementation
import sys
import fileinput
import strip_comments

class VorberGCC:
    def __init__(self, verbose = False):
        self.reset(verbose)
  
    def __str__(self):
        regs = 'Regs: c:{0} s:{1} d:{2} e:{3}'.format(self.reg_c, self.reg_s, self.reg_d, self.reg_e)
        ds = 'Data: ' + str(self.data_stack)
        cs = 'Ctrl: ' + str(self.ctrl_stack)
        es = 'Env:  ' + str(self.env_stack)
        result = '\n'.join((regs, ds, cs, es, 'state: ' + self.state))
        return result

    def reset(self, verbose = False):
        '''
        Resets itself to initial state
        Specifying verbose=True enables diagnostics spam via prints
        '''
        self.reg_c = 0
        self.reg_s = 0
        self.reg_d = 0
        self.reg_e = -1 #because 0 already points at valid place in env_stack, which is empty now
        self.data_stack = []
        self.ctrl_stack = []
        self.env_stack = []
        self.program = []    
        self.terminal_state = False
        self.state = 'empty'
        self.verbose = verbose

    def load(self, code_lines):
        '''
        Loads program from a list of lines.
        Resets itself before loading and places TAG_STOP on ctrl_stack
        
        code_lines: a list of lines.
            empty lines, comments (;<comment>) and any kinds of whitespace allowed
        '''
        self.reset(self.verbose)
        self.program = filter(lambda s: len(s) > 0, map(str.strip, strip_comments.strip_comments(code_lines)))
        self.state = 'loaded'
        self.ctrl_stack.append({'tag':'TAG_STOP'}) # to be able to stop with RTN without popping an empty stack
        self.__log(str(self))
        
    def step(self):
        '''
        Executes a single instruction at current %c
        '''
        if self.state == 'error':
            self.__log('step called while in error state')
            return
        command_line = self.program[self.reg_c]
        self.__log('step ' + str(self.reg_c) + ' line:' + command_line)
        parts = command_line.split()
        cmd = parts[0]
        args = parts[1:]
        self.__process_cmd(cmd, map(int, args))
    
    def run(self):
        '''
        Runs the program from current position to termination
        Termination can happen due to any error, STOP command or popping TAG_STOP during RTN
        '''
        self.state = 'executing'
        while not self.terminal_state:
            self.__log(str(self))
            self.step()
        self.__log(str(self))

        
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
            
    def __process_cmd(self, cmd, args):
        if cmd == 'LDC':
            self.data_stack.append({'tag':'int', 'value':int(args[0])})
            self.reg_c += 1
        elif cmd == 'LD':
            fp = self.env_stack[-1]
            n = args[0]
            i = args[1]
            while n > 0:
                fp = self.env_stack[fp['parent']]
                n -= 1
            if fp['frame_tag'] == 'TAG_DUM': 
                self.__error('FRAME_MISMATCH')
                return
            v = fp['values'][i]
            self.data_stack.append(v)
            self.reg_c += 1
        elif cmd == 'ADD':
            self.__process_arithmetic_cmd(lambda a,b:a+b)
        elif cmd == 'SUB':
            self.__process_arithmetic_cmd(lambda a,b:a-b)
        elif cmd == 'MUL':
            self.__process_arithmetic_cmd(lambda a,b:a*b)
        elif cmd == 'DIV':
            self.__process_arithmetic_cmd(lambda a,b:a/b)
        elif cmd == 'CEQ':
            self.__process_arithmetic_cmd(lambda a,b: 1 if a==b else 0)
        elif cmd == 'CGT':
            self.__process_arithmetic_cmd(lambda a,b: 1 if a>b else 0)
        elif cmd == 'CGTE':
            self.__process_arithmetic_cmd(lambda a,b: 1 if a>=b else 0)
        elif cmd == 'ATOM':
            x = self.data_stack.pop()
            self.data_stack.append({'tag':'int', 'value': 1 if x['tag'] == 'int' else 0})
            self.reg_c += 1
        elif cmd == 'CONS':
            y = self.data_stack.pop()
            x = self.data_stack.pop()
            self.data_stack.append({'tag':'cons', 'value':(x,y)})
            self.reg_c += 1
        elif cmd == 'CAR':
            self.__process_extract_cons(0)
        elif cmd == 'CDR':
            self.__process_extract_cons(0)
        elif cmd == 'SEL':
            x = self.data_stack.pop()
            self.__match_tag(x, 'int')
            if self.terminal_state:
                return
            self.ctrl_stack.append({'tag':'join', 'value':self.reg_c+1})
            self.reg_c = args[1 if x == 0 else 0]
        elif cmd == 'JOIN':
            x = self.ctrl_stack.pop()
            if x['tag'] != 'join':
                self.__error('CONTROL_MISMATCH')
                return
            self.reg_c = x
        elif cmd == 'LDF':
            closure = (args[0],self.reg_e)
            self.data_stack.append({'tag':'closure','value':closure})
            self.reg_c += 1
        elif cmd == 'AP':
            x = self.data_stack.pop()
            self.__match_tag(x,'closure')
            if self.terminal_state:
                return
            f = x['value'][0]
            e = x['value'][1]
            fp = {'frame_tag':'FRAME_NO_TAG', 'parent':e, 'values':[{} for i in range(args[0])], 'size':args[0]}
            i = args[0]-1
            while i != -1:
                y = self.data_stack.pop()
                fp['values'][i] = y
                i -= 1
            self.ctrl_stack.append({'tag':'WTFNOTAG!11AP', 'value':self.reg_e}) 
            self.ctrl_stack.append({'tag':'TAG_RET', 'value':self.reg_c+1})
            self.env_stack.append(fp)
            self.reg_e += 1 #len(self.env_stack) - 1
            self.reg_c = f
        elif cmd == 'RTN':
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
        elif cmd == 'DUM':
            fp = {'frame_tag':'TAG_DUM','parent':self.reg_e, 'values':[{} for i in range(args[0])], 'size':args[0]}
            self.env_stack.append(fp)
            self.reg_e += 1
            self.reg_c += 1
        elif cmd == 'RAP':
            x = self.data_stack.pop()
            self.__match_tag(x,'closure')
            if self.terminal_state:
                return

            f = x['value'][0]
            fp = x['value'][1]

            ef = self.env_stack[self.reg_e]
            if ef['frame_tag'] != 'TAG_DUM' or ef['size'] != args[0] or self.reg_e != fp:
                self.__error('FRAME_MISMATCH')
            i = args[0] - 1
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
        elif cmd == 'STOP':
            self.terminal_state=True
        else:
            self.__error('UNKNOWN CMD')
           
def main():
    gcc = VorberGCC(verbose=True)
    gcc.load([line for line in fileinput.input()])
    gcc.run()
    
if __name__ == '__main__':
    main()