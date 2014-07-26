class GCCInterface(object):
    def initialize(self, world_state, undocumented):
        '''world_state must be an opaque handle constructed via marshall_* methods.
        returns (ai_state, step_function)'''
    
    def step(self, ai_state, world_state):
        '''returns ai_state, move. Move is an already decoded integer.'''

    def marshall_int(self, i):
        'Return an opaque handle representing i'
    
    def marshall_cons(self, car, cdr):
        'Return an opaque handle representing (car, cdr)'


class GCCWrapper:
    def __init__(self, gcc):
        assert isinstance(gcc, GCCInterface)
        self.gcc = gcc
        
    
    def initialize(self, world, undocumented):
        world_state = self.marshall_world_state(world)
        self.ai_state, self.step_function = self.gcc.initialize(world_state, undocumented)
            
    
    def step(self, world):
        world_state = self.marshall_world_state(world)
        self.ai_state, move = self.gcc.step(self.ai_state, world_state)
        return move
        
    
    def marshall_world_state(self, world):
        # convert world_state to the list/tuple/int representation
        world_state = world
        # go implement the above, lol
        
        gcc = self.gcc
        def rec(item):
            if isinstance(item, int):
                return gcc.marshall_int(item)
            
            if isinstance(item, tuple):
                curr = None
            elif isinstance(item, list):
                curr = gcc.marshall_int(0)
            else:
                assert False
                
            for it in reversed(item):
                it = rec(it)
                if curr is None:
                    curr = it
                else:
                    curr = gcc.marshall_cons(it, curr)
            return curr
        return rec(world_state)

