class GCCInterface(object):
    def call(self, address_or_closure, *args):
        'Call a function. Put args on the data stack, return contents of the data stack after the function returns'

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
        self.ai_state, self.step_function = self.gcc.call(0, world_state, undocumented)
            
    
    def get_move(self, world):
        world_state = self.marshall_world_state(world)
        self.ai_state, move = self.gcc.call(self.step_function, self.ai_state, world_state)
        return move
        
    
    def marshall_world_state(self, world):
        # convert world_state to the list/tuple/int representation
        world_state = self.convert_world_state(world)

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

    def convert_world_state(self, world):
        return (self.encode_map(world),
                self.encode_lman(world),
                self.encode_ghosts(world),
                world.remaining_fruit_ticks())

    def encode_map(self, world):
        return [self.encode_map_row(world, y) for y in range(world.height())]

    def encode_map_row(self, world, y):
        return [world.at(x, y) for x in range(world.width())]

    def encode_lman(self, world):
        lman = world.lambdamen[0]
        return (world.remaining_power_pill_ticks(),
                (lman.x, lman.y),
                lman.direction,
                lman.lives,
                lman.score)

    def encode_ghosts(self, world):
        return [(ghost.vitality, (ghost.x, ghost.y), ghost.direction)
                for ghost in world.ghosts]
