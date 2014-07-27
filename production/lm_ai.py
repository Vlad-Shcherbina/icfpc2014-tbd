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


class Humanoid(game.LambdaManAI):
    """ By default, continue moving in the same direction (following bends),
        unless we are being chased by a ghost, in which case flee. At a
        junction, choose to move in the direction where we see the most number
        of pills/fruit in the straight line leading from the junction. """
    def get_move(self, map):
        open_directions = self.get_open_directions(map)
        if not open_directions:
            raise Exception("ZAMUROVALI DEMONY!")

        if len(open_directions) == 1:
            return open_directions[0]

        if not self.ghosts_frightened(map):
            safe_directions = [
                d for d in open_directions
                if self.distance_to_ghost(map, d) == map.width()]
        else:
            safe_directions = open_directions

        if len(safe_directions) == 1:
            return safe_directions[0]

        if len(open_directions) == 2:
            # If we have just two possible directions, prefer to follow the path
            # rather than turn around.
            if map.lambdaman.direction == game.OPPOSITE_DIRECTIONS[open_directions[0]]:
                return open_directions[1]
            else:
                return open_directions[0]

        max_value = 0
        max_net_value = 0
        best_direction = open_directions[0]
        best_net_direction = open_directions[0]
        for d in open_directions:
            value, penalty = self.expected_value(map, d)
            if value > max_value:
                best_direction = d
                max_value = value
            if value - penalty > max_net_value:
                best_net_direction = d
                max_net_value = value - penalty
        if max_net_value > 0:
            return best_net_direction
        return best_direction

    def get_open_directions(self, map):
        result = []
        for direction in range(4):
            cell = map.at(map.lambdaman.x + game.DELTA_X[direction],
                          map.lambdaman.y + game.DELTA_Y[direction])
            if cell:
                result.append(direction)
        return result

    def ghosts_frightened(self, map):
        return map.ghosts[0].vitality == game.FRIGHT

    def ghost_at(self, map, x, y):
        return any(g for g in map.ghosts if g.x == x and g.y == y)

    def distance_to_ghost(self, map, direction):
        for x, y, distance in self.iterate_cells_until_wall(map, direction):
            if self.ghost_at(map, x, y):
                return distance
        return map.width()

    def iterate_cells_until_wall(self, map, direction):
        dx = game.DELTA_X[direction]
        dy = game.DELTA_Y[direction]
        x = map.lambdaman.x
        y = map.lambdaman.y
        distance = 0
        while True:
            x += dx
            y += dy
            distance += 1
            if x < 0 or x >= map.width() or y < 0 or y >= map.height():
                break
            if map.at(x, y) == game.WALL:
                break
            yield x, y, distance

    def expected_value(self, map, direction):
        result = 0
        penalty = 0
        for x, y, distance in self.iterate_cells_until_wall(map, direction):
            cell = map.at(x, y)
            if cell == game.PILL:
                result += 10
            elif cell == game.POWER_PILL:
                result += 50
            elif cell == game.FRUIT:
                result += 100
            elif cell == game.EMPTY and result <= 0:
                # Penalize empty cells that we need to go through in order to
                # reach the pills.
                penalty += 10
        return result, penalty
