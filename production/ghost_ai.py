import random
import logging
import game


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
