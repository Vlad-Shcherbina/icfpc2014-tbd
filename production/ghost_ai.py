import random
import logging
import game

logger = logging.getLogger(__name__)

DIRECTION_S = ['UP', 'RIGHT', 'DOWN', 'LEFT']

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


class GhostAI_Shortest(GhostAI_Py):
    def __init__(self, map, index):
        super(GhostAI_Shortest, self).__init__(map, index)

    def run(self, ghc):
        index = ghc.get_index()
        (x, y) = ghc.get_ghost_pos(index)
        (man_x, man_y) = ghc.get_man_pos()
        dx = man_x - x
        dy = man_y - y
        adx = dx * dx
        ady = dy * dy
        if adx > ady:
            ghc.set_direction(game.RIGHT if dx > 0 else game.LEFT)
        else:
            ghc.set_direction(game.DOWN if dy > 0 else game.UP)
        logger.debug("ghost %d @ (%d, %d) to (%d, %d) chose %s",
                     index, x, y, man_x, man_y,  DIRECTION_S[ghc.direction])


class GhostAI_Original(GhostAI_Py):
    def __init__(self, map, index):
        super(GhostAI_Original, self).__init__(map, index)
        self.rng = random.Random(42)

    def chase_target(self, ghc):
        # maximum distance on a map
        score = 255 * 255 * 2

        for direction in game.DIRECTIONS:
            if direction == self.opposite:
                continue

            next_x = self.x + game.DELTA_X[direction]
            next_y = self.y + game.DELTA_Y[direction]
            if ghc.get_map(next_x, next_y) == game.WALL:
                continue

            dx = next_x - self.target_x
            dy = next_y - self.target_y

            # considering 8 bit registers this is crap
            d = dx * dx + dy * dy

            logger.debug("ghost %d @ (%d, %d) chases (%d, %d) score %d, %s %d",
                         self.index, self.x, self.y, self.target_x, self.target_y,
                         score, DIRECTION_S[direction], d)

            if score > d:
                ghc.set_direction(direction)
                score = d
                logger.debug("ghost %d @ (%d, %d) chases (%d, %d) chose %s",
                             self.index, self.x, self.y, self.target_x, self.target_y,
                             DIRECTION_S[ghc.direction])

    def choose_random(self, ghc):
        valid = 0
        valid_len = 0

        for direction in game.DIRECTIONS:
            if direction == self.opposite:
                continue

            next_x = self.x + game.DELTA_X[direction]
            next_y = self.y + game.DELTA_Y[direction]
            if ghc.get_map(next_x, next_y) == game.WALL:
                continue

            logger.debug("ghost %d @ (%d, %d) has %s choice",
                     self.index, self.x, self.y, DIRECTION_S[direction])
            valid_len += 1
            valid |= 1 << direction

        if valid_len <= 1:
            return

        direction = 0
        idx = self.rng.randint(1, valid_len)
        while idx > 0:
            while valid & 1 == 0:
                direction += 1
                valid >>= 1
            idx -= 1

        ghc.set_direction(direction)
        logger.debug("ghost %d @ (%d, %d) random chose %s",
                     self.index, self.x, self.y,
                     DIRECTION_S[direction])

    def run(self, ghc):
        self.index = ghc.get_index()
        (self.x, self.y) = ghc.get_ghost_pos(self.index)
        (vitality, direction) = ghc.get_ghost_stat(self.index)
        self.opposite = game.OPPOSITE_DIRECTIONS[direction]

        if vitality == game.FRIGHT:
            self.choose_random(ghc)
            return

        self.character(ghc)


class GhostAI_Random(GhostAI_Original):
    def __init__(self, map, index):
        super(GhostAI_Random, self).__init__(map, index)

    def character(self, ghc):
        self.choose_random(ghc)


class GhostAI_Red(GhostAI_Original):
    'simply chases pacman'

    def __init__(self, map, index):
        super(GhostAI_Red, self).__init__(map, index)

    def character(self, ghc):
        (self.target_x, self.target_y) = ghc.get_man_pos()
        self.chase_target(ghc)


class GhostAI_Pink(GhostAI_Original):
    'chases a tile 4 tiles ahead of pacman'

    def __init__(self, map, index):
        super(GhostAI_Pink, self).__init__(map, index)
        self.old_x = 0

    def character(self, ghc):
        (man_x, man_y) = ghc.get_man_pos()
        if self.old_x != 0:
            dx = man_x - self.old_x
            dy = man_y - self.old_y

            logger.debug("ghost %d @ (%d, %d) tracks (%d + %d, %d + %d)",
                         self.index, self.x, self.y,
                         self.old_x, dx,
                         self.old_y, dy)

            self.target_x = man_x + dx * 4
            self.target_y = man_y + dy * 4
            self.chase_target(ghc)

        self.old_x = man_x
        self.old_y = man_y
