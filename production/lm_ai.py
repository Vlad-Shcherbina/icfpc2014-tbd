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

class TunnelDigger(game.LambdaManAI):
    def __init__(self):
        self.rng = random.Random(42)

    def get_move(self, world):
        lm = world.lambdaman

        best_score = -1
        best_dir = -1
        for d in game.DIRECTIONS:
            dx, dy = game.DELTA_X[d], game.DELTA_Y[d]

            def after(s):
                return (lm.x + s * dx, lm.y + s * dy)

            # find distance to wall
            towall = 1
            while world.at(*after(towall)) != game.WALL: towall += 1

            # find distance to closest ghost
            i = 1
            dist_ghost = 1024
            while i != towall:
                ix, iy = after(i)
                for g in world.ghosts:
                    if (g.vitality == game.STANDARD) and (g.x, g.y) == (ix, iy):
                        if g.direction != d:
                            dist_ghost = min(dist_ghost, (i + 1) / 2)
                        else:
                            dist_ghost = min(dist_ghost, (towall + 1) / 2)
                i += 1

            if dist_ghost <= 2:
                score_here = -1
            else:
                score_here = 0
                i = 1
                while i != towall:
                    if i >= dist_ghost: break
                    ix, iy = after(i)

                    for g in world.ghosts:
                        if (g.vitality == game.FRIGHT) and (g.x, g.y) == (ix, iy):
                            score_here += 5

                    tp = world.at(ix, iy)
                    if tp == game.PILL:
                        score_here += 1
                    elif tp == game.POWER_PILL:
                        score_here += 10
                    elif tp == game.FRUIT:
                        score_here += 3
                    i += 1

            if score_here > best_score:
                best_score, best_dir = score_here, d

        if best_score > 0:
            return best_dir

        if world.at(lm.x + game.DELTA_X[lm.direction], lm.y + game.DELTA_Y[lm.direction]) != game.WALL:
            return lm.direction
        return self.rng.choice(game.DIRECTIONS)



