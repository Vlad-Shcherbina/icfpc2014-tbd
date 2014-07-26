class GCCInterface(object):
    def load(self, code):
        '''
        Loads the code into gcc
        '''
        pass
    def run(self):
        '''
        Runs the loaded code
        '''
        pass

    def pop_data_cons(self):
        '''
        Method to pop cons from data stack
        intended usage is to retrieve program result after it is finished
        '''
        pass
    def pop_data_closure(self):
        '''
        Method to pop closure from data stack
        intended usage is to retrieve program result after it is finished
        '''
        pass
    def set_ip(self, ip):
        '''
        Sets instruction pointer (register %c) to specified instruction
        '''
        pass
    def set_env(self, e):
        '''
        Sets environment pointer
        '''
        pass
    def add_env_cons(self, ep, t):
        '''
        Adds a 2-element tuple to environment
        ep: environment pointer
        t: tuple
        '''
        pass

class GCCWrapper(object):
    def __init__(self, gcc, code):
        self.gcc = gcc
        gcc.load(code)
        
    def initialize(self, world_state, udefined):
        #prepare input params for gcc
        #it seems they should be put onto env_stack
        self.gcc.set_env(0)
        self.gcc.set_env_cons(0,world_state_to_cons(world_state))
        self.gcc.set_env_cons(0,undefined_cons(undefined))
        #initial run to get step and ai state
        self.gcc.run()
        #get result from data stack, resut is a closure cell
        ret = gcc.pop_data_cons()
        self.ai_state = ret[0]
        self.closure = ret[1]
        
    def eval(world_state, undefined):
        #all further evals after initialize go as follows
        #set up machine to run the closure it returned 
        #that is set %c, %e to what it should be, and fill env
        self.gcc.set_ip(self.closure[0])
        self.gcc.set_env(self.closure[1])
        self.gcc.set_env_cons(self.closure[1], ai_state)
        self.gcc.set_env_cons(self.closure[1], world_state_to_cons(world_state))
        #then run the machine and extract new state and direction
        self.gcc.run()
        ret = self.gcc.pop_data_cons()
        self.ai_state = ret[0]
        direction = ret[1]
        return direction
    def undefined_cons(undefined):
        return (0,0)
    def world_state_to_cons(world_state):
        pass