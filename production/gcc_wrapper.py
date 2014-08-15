import logging
logger = logging.getLogger(__name__)

from abc import abstractmethod, ABCMeta

import game
from gcc_utils import deep_unmarshal, lto_to_cons, is_cons, cons_to_list, cons_to_mat


class InterpreterException(Exception):
    pass


class GCCInterface(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def call(self, address_or_closure, *args, **kwargs):
        '''Call a function. Put args into a new environment frame, return the top of the data stack after the function returns.
        Args and the return value are automatically marshalled.'''

    @abstractmethod
    def marshal(self, x):
        '''Return an opaque handle representing i, which can be an int or a two-element tuple.
        Shallow, so the elements of the tuple must be marshalled handles.'''


    @abstractmethod
    def unmarshal(self, x):
        '''If x is an opaque handle representing an int or cons, unmarshal (shallowly for cons) and return it.
        Otherwise return the opaque handle unchanged.
        This could cause problems for unmarshall_deep if we had a GCC representing opaque handles as raw tuples, but we don't.
        '''

    def last_call_ticks(self):
        'Return the number of ticks taken to execute the last call'
        return 0


class GCCWrapper(object):
    def __init__(self, gcc):
        assert isinstance(gcc, GCCInterface)
        self.gcc = gcc
        self.total_step_ticks = 0
        self.max_step_ticks = 0
        self.moves = 0

    def initialize(self, world, undocumented):
        world_state = self.marshal_world_state(world)
        self.ai_state, self.step_function = self.gcc.call(0, world_state, undocumented, max_ticks=game.MAX_TICKS_INIT)
        self.init_ticks = self.gcc.last_call_ticks()

    def get_move(self, world):
        gcc = self.gcc
        world_state = self.marshal_world_state(world)
        self.ai_state, move = gcc.call(self.step_function, self.ai_state, world_state, max_ticks=game.MAX_TICKS)
        ticks = gcc.last_call_ticks()
        self.moves += 1
        self.total_step_ticks += ticks
        if ticks > self.max_step_ticks:
            self.max_step_ticks = ticks

        self.log_ai_state(self.ai_state)
        return move


    @staticmethod
    def log_ai_state(ai_state):
        if is_cons(ai_state) and ai_state[0] == 999888777: # password from ff.py
            field = ai_state[1]
            field = [cons_to_mat(row)
                     for row in cons_to_list(field)]
            logger.info('ff field state:')
            for line in field:
                s = ''
                for e in line:
                    s += '{:6}'.format(e)
                logger.info(s)
        else:
            logger.info('ai state: {}'.format(ai_state))


    def get_vm_statistics(self):
        return game.GccStats(
            init=self.init_ticks,
            avg=1.0 * self.total_step_ticks / self.moves if self.moves else 0,
            total=self.max_step_ticks)


    def marshal_world_state(self, world):
        world_state = self.convert_world_state(world)
        return lto_to_cons(world_state)


    def convert_world_state(self, world):
        '''convert world_state to the list/tuple/int representation'''
        return (self.encode_map(world),
                self.encode_lman(world),
                self.encode_ghosts(world),
                world.remaining_fruit_ticks())


    def encode_map(self, world):
        result = [self.encode_map_row(world, y) for y in range(world.height())]
        if world.fruit_spawn is not None:
            x, y = world.fruit_spawn
            result[y][x] = game.FRUIT
        return result


    def encode_map_row(self, world, y):
        return [world.at(x, y) for x in range(world.width())]


    def encode_lman(self, world):
        lman = world.lambdaman
        return (world.remaining_power_pill_ticks(),
                (lman.x, lman.y),
                lman.direction,
                lman.lives,
                lman.score)


    def encode_ghosts(self, world):
        return [(ghost.vitality, (ghost.x, ghost.y), ghost.direction)
                for ghost in world.ghosts]
