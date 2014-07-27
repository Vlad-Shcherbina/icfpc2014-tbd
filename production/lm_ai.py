import game
import random
import logging


logger = logging.getLogger(__name__)


class Oscillating(game.LambdaManAI):
    def __init__(self, frequency):
        assert frequency >= 1
        self.frequency = frequency
        self.cnt = 0

    def get_move(self, map):
        self.cnt += 1
        if self.cnt % (2 * self.frequency) < self.frequency:
            return game.LEFT
        else:
            return game.RIGHT


class NearestPill(game.LambdaManAI):
    def __init__(self, straight=False):
        self.rng = random.Random(42)
        self.straight = straight

    def get_move(self, map):
        lm = map.lambdaman
        best_score = -1
        best_dir = -1
        for d in game.DIRECTIONS:
            dx = game.DELTA_X[d]
            dy = game.DELTA_Y[d]
            target = map.at(lm.x + dx, lm.y + dy)
            target_score = {game.PILL: 1, game.POWER_PILL: 2, game.FRUIT: 2}.get(target, -1)
            if best_score < target_score:
                best_score = target_score
                best_dir = d
                pass
        if best_score > 0:
            return best_dir

        if self.straight:
            nx = map.lambdaman.x + game.DELTA_X[map.lambdaman.direction]
            ny = map.lambdaman.y + game.DELTA_Y[map.lambdaman.direction]
            if map.at(nx, ny) != game.WALL:
                return map.lambdaman.direction
            else:
                return self.rng.choice(game.DIRECTIONS)
        else:
            return self.rng.choice(game.DIRECTIONS)
