class wrapper_to_gcc_interface:
    def load(code):
        '''
        Loads the code into gcc
        '''
        pass
    def run():
        '''
        Runs the loaded code
        '''
        pass
    def push_data_int(i):
        '''
        Method to push int value on gcc data stack
        i should be int
        '''
        pass
    def push_data_cons(t):
        '''
        Method to push 2-element tuple on gcc data stack
        t should be tuple with exactly 2 elements
        '''
        pass
    def pop_data_int():
        '''
        Method to pop int from data stack
        intended usage is to retrieve program result after it is finished
        '''
        pass
    def pop_data_cons():
        '''
        Method to pop cons from data stack
        intended usage is to retrieve program result after it is finished
        '''
        pass
    def pop_data_closure():
        '''
        Method to pop closure from data stack
        intended usage is to retrieve program result after it is finished
        '''
        pass
    def set_ip(ip)
        '''
        Sets instruction pointer (register %c) to specified instruction
        '''
        pass
    def set_env(e):
        '''
        Sets environment pointer
        '''
        pass
    def add_env_cons(ep, t):
        '''
        Adds a 2-element tuple to environment
        ep: environment pointer
        t: tuple
        '''
        pass

class gcc_wrapper:
    def __init__(gcc, code, world_state, undefined):
        self.gcc = gcc
        gcc.load(code)
        initialize(world_state, undefined)
        
    def initialize(world_state, udefined):
        #prepare input params for gcc
        #it seems they should be put onto env_stack
        gcc.run()
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
        
    def world_state_to_cons(world_state):
        pass