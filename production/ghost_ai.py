import random
import logging

import game
from log_context import log_context


logger = logging.getLogger(__name__)


class BasePyAI(object):

    def initialize(self, map, index):
        self.map = map
        self.index = index
        self.ghost = map.ghosts[index]
        self.rng = random.Random(42)

    def get_move(self):
        raise NotImplementedError()


class GhostAI_Random(BasePyAI):

    def get_move(self):
        return self.rng.choice(game.DIRECTIONS)


class GhostAI_Shortest(BasePyAI):

    def get_move(self):
        dx = self.map.lambdaman.x - self.ghost.x
        dy = self.map.lambdaman.y - self.ghost.y
        if abs(dx) > abs(dy):
            return game.RIGHT if dx > 0 else game.LEFT
        else:
            return game.DOWN if dy > 0 else game.UP


class BaseChaser(BasePyAI):

    def chase(self, target_x, target_y):
        # maximum distance on a map
        score = 255 * 255 * 2

        best_direction = self.rng.choice(game.DIRECTIONS)

        for direction in game.DIRECTIONS:
            if direction == game.OPPOSITE_DIRECTIONS[self.ghost.direction]:
                continue

            next_x = self.ghost.x + game.DELTA_X[direction]
            next_y = self.ghost.y + game.DELTA_Y[direction]
            if self.map.at(next_x, next_y) == game.WALL:
                continue

            dx = next_x - target_x
            dy = next_y - target_y

            d = dx * dx + dy * dy

            if score > d:
                best_direction = direction
                score = d
        return best_direction

    def choose_random(self):
        directions = []
        for d in game.DIRECTIONS:
            if d == game.OPPOSITE_DIRECTIONS[self.ghost.direction]:
                continue
            next_x = self.ghost.x + game.DELTA_X[d]
            next_y = self.ghost.y + game.DELTA_Y[d]
            if self.map.at(next_x, next_y) == game.WALL:
                continue
            directions.append(d)
        if not directions:
            directions = game.DIRECTIONS
        return self.rng.choice(directions)

    def get_move(self):
        if self.ghost.vitality == game.STANDARD:
            return self.chase(*self.get_target())
        else:
            target = self.map.lambdaman.x, self.map.lambdaman.y
            return game.OPPOSITE_DIRECTIONS[
                self.chase(*target)]


class GhostAI_Red(BaseChaser):
    'simply chases pacman'

    def get_target(self):
        return self.map.lambdaman.x, self.map.lambdaman.y


class GhostAI_Pink(BaseChaser):
    'simply chases pacman'

    def get_target(self):
        return (
            self.map.lambdaman.x + 4 * game.DELTA_X[self.map.lambdaman.direction],
            self.map.lambdaman.y + 4 * game.DELTA_Y[self.map.lambdaman.direction])


def in_front(actor, distance):
    return (
        actor.x + game.DELTA_X[actor.direction] * distance,
        actor.y + game.DELTA_Y[actor.direction] * distance)


def dir_to(actor1, actor2):
    dx = actor2.x - actor1.x
    dy = actor2.y - actor1.y
    if abs(dx) > abs(dy):
        return game.RIGHT if dx > 0 else game.LEFT
    else:
        return game.DOWN if dy > 0 else game.UP


class Hunter(BasePyAI):
    """ Follows trail. """

    def __init__(self):
        self.prev_lm_dir = 0
        self.trail = []

    def find_trail(self, loc):
        for i, t in enumerate(self.trail):
            if t[0] == loc:
                return (i,) + t
        lm = self.map.lambdaman
        if loc == (lm.x, lm.y):
            return (1000, loc, 42)
        return (-1, (0, 0), 1)

    def trace(self, dir):
        dx = game.DELTA_X[dir]
        dy = game.DELTA_Y[dir]
        x = self.ghost.x
        y = self.ghost.y
        best_trail = (-1, (0, 0), 1)
        while True:
            x += dx
            y += dy
            if self.map.at(x, y) == game.WALL:
                break
            tr = self.find_trail((x, y))
            if tr > best_trail:
                best_trail = tr
        rec_dir = best_trail[2]
        if game.OPPOSITE_DIRECTIONS[dir] != rec_dir:
            rec_dir = dir
        return best_trail[0], rec_dir

    def get_move(self):
        with log_context('hunter#{}'.format(self.index)):
            lm = self.map.lambdaman
            if self.ghost.vitality != game.STANDARD:
                logging.info('fleeing')
                return dir_to(lm, self.ghost)

            logger.info('current coords: {}'.format((self.ghost.x, self.ghost.y)))
            logger.info('current pacman state: {}'.format((lm.x, lm.y, lm.direction)))

            if lm.direction != self.prev_lm_dir:
                self.prev_lm_dir = lm.direction
                self.trail.append((in_front(lm, -1), lm.direction))
                logging.info('updating trail: {}'.format(self.trail))

            tr = self.find_trail((self.ghost.x, self.ghost.y))
            if tr[0] > -1:
                logging.info('standing on a trail {}'.format(tr))
            best_trail = tr[0], min(tr[2], 3)

            for d in game.DIRECTIONS:
                tr = self.trace(d)
                if tr[0] > -1:
                    logging.info('see trail {}'.format(tr))
                if tr > best_trail:
                    best_trail = tr
            if best_trail[0] > -1:
                logging.info('following trail in dir {}'.format(best_trail[1]))
                return best_trail[1]
            else:
                return dir_to(self.ghost, lm)


class Splitter(BasePyAI):
    '''Uniformly splits at each junction'''

    def look_around(self):
        directions = []
        packman = []
        # *2 and slice is here to rotate based on the direction
        for delta_x, delta_y, direction in zip(game.DELTA_X, game.DELTA_Y, game.DIRECTIONS):
            if direction == game.OPPOSITE_DIRECTIONS[self.ghost.direction]:
                continue
            content = self.map.at(self.ghost.x + delta_x, self.ghost.y + delta_y)
            if self.map.lambdaman.x == self.ghost.x + delta_x and self.map.lambdaman.y == self.ghost.y + delta_y:
                packman = [direction]
            elif content != 0:
                directions.append(direction)
        return packman, directions

    def get_move(self, magic=None):
        if not magic:
            magic = self.index
        packman, directions = self.look_around()
        if len(directions) + len(packman) < 2:
            # We have no choice
            return self.ghost.direction
        elif packman and self.ghost.vitality != game.FRIGHT:
            # Get him!
            return packman[0]
        # rotate directions list based on current direction
        shift = self.ghost.direction % len(directions)
        directions = (directions * 2)[shift:shift + len(directions)]
        logger.info(','.join([str(i) for i in directions]))
        return directions[magic % len(directions)]


class RedSplitter(BasePyAI):
    def initialize(self, map, index):
        super(RedSplitter, self).initialize(map, index)
        #self.red = GhostAI_Red()
        with open('../data/ghosts/red.ghc') as fin:
            code = fin.read()
        self.red = game.GhostAI(code)
        self.splitter = Splitter()
        self.red.initialize(map, index)
        self.splitter.initialize(map, index)

    def get_move(self):
        magic = 0
        splitter = 0
        for ghost in self.map.ghosts:
            if ghost.index == self.index:
                magic = splitter
            elif abs(ghost.x - self.ghost.x) + abs(ghost.y - self.ghost.y) < 2:
                splitter += 1
        if splitter:
            logger.info("Ghost %d in splitter mode with magic %d" % (self.index, magic))
            return self.splitter.get_move(magic)
        else:
            return self.red.get_move()
