import random
import logging

logger = logging.getLogger(__name__)

UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

class GHC_Ints:
    def __init__(self, map, index):
        self.map = map
        self.index = index
        self.direction = None

    def set_direction(self, direction):
        'INT 0'
        self.direction = direction

    def get_man_pos(self):
        'INT 1', 'INT 2'
        man = self.map.lambdamen[0]
        return (man.x, man.y)

    def get_index(self):
        'INT 3'
        return self.index

    def get_ghost_start_pos(self, index):
        'INT 4'
        ghost = self.map.ghosts[index]
        return (ghost.start_x, ghost.start_y)

    def get_ghost_pos(self, index):
        'INT 5'
        ghost = self.map.ghosts[index]
        return (ghost.x, ghost.y)

    def get_ghost_stat(self, index):
        'INT 6'
        ghost = self.map.ghosts[index]
        return (ghost.vitality, ghost.direction)

    def get_map(self, x, y):
        'INT 7'
        return self.map.at(x, y)

    def debug(self):
        'INT 8'
        pass


class GhostAI_Py(object):
    def __init__(self, map, index):
        self.ghc = GHC_Ints(map, index)

    def get_move(self):
       self.run(self.ghc)
       return self.ghc.direction

    def run(self, ghc):
        pass

class GhostAI_Random(GhostAI_Py):
    def __init__(self, map, index):
        super(GhostAI_Random, self).__init__(map, index)

    def fun(self, ghc):
        ghc.set_direction(random.randint(0, 3))

class GhostAI_Shortest(GhostAI_Py):
    def __init__(self, map, index):
        super(GhostAI_Shortest, self).__init__(map, index)

    def run(self, ghc):
        index = ghc.get_index()
        (x, y) = ghc.get_ghost_pos(index)
        (man_x, man_y) = ghc.get_man_pos()
        dx = man_x - x
        dy = man_y - y
        adx = dx if dx > 0 else -dx
        ady = dy if dy > 0 else -dy
        if adx > ady:
            ghc.set_direction(RIGHT if dx > 0 else LEFT)
        else:
            ghc.set_direction(DOWN if dy > 0 else UP)
        logger.info("ghost %d @ (%d, %d) to (%d, %d) chose %d",
                    index, x, y, man_x, man_y, ghc.direction)
