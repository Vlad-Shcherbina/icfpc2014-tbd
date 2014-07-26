import game
import random


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
    def __init__(self):
        self.rng = random.Random(42)

    def get_move(self, map):
        lm = map.lambdaman
        for d in game.DIRECTIONS:
            dx = game.DELTA_X[d]
            dy = game.DELTA_Y[d]
            target = map.at(lm.x + dx, lm.y + dy)
            if target in [game.PILL, game.POWER_PILL, game.FRUIT]:
                return d

        return self.rng.choice(game.DIRECTIONS)
