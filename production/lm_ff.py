import random
import logging
import pprint
import copy

import game

from log_context import log_context


logger = logging.getLogger(__name__)


class ForceField(game.LambdaManAI):
    def __init__(self):
        self.first_call = False

    def initialize(self, map, undocumented):
        self.f = [[DEFAULT_CELL] * map.width() for _ in range(map.height())]

    def get_move(self, map):
        for _ in range(10):
            self.f = diffuse(self.f)
            self.f = merge(self.f, map)
            self.f = merge_ghosts(self.f, map.ghosts)

        logger.info('field:\n{}'.format(pprint.pformat(self.f)))

        best_dir = 0
        best_score = -1
        for dir in game.DIRECTIONS:
            nx = map.lambdaman.x + game.DELTA_X[dir]
            ny = map.lambdaman.y + game.DELTA_Y[dir]
            if best_score < self.f[ny][nx]:
                best_score = self.f[ny][nx]
                best_dir = dir
        logger.info('best dir {}'.format(best_dir))
        return best_dir


def diffuse(f):
    f = shift_left(f)
    f1 = shift_right(shift_up(f))
    f = combine(f, f1)
    f1 = shift_right(shift_down(f))
    f = combine(f, f1)
    return decrement(f)


DEFAULT_CELL = 0

def shift_left(f):
    return [line[1:] + [DEFAULT_CELL] for line in f]

def shift_right(f):
    return [[DEFAULT_CELL] + line[:-1] for line in f]

def shift_up(f):
    return f[1:] + [[DEFAULT_CELL] * len(f[0])]

def shift_down(f):
    return [[DEFAULT_CELL] * len(f[0])] + f[:-1]

def combine(f1, f2):
    assert len(f1) == len(f2)
    result = []
    for line1, line2 in zip(f1, f2):
        result.append([])
        assert len(line1) == len(line2)
        for c1, c2 in zip(line1, line2):
            result[-1].append(combine_cell(c1, c2))
    return result

def decrement(f):
    return [map(decrement_cell, line) for line in f]


def combine_cell(f1, f2):
    return max(f1, f2)

def decrement_cell(f_cell):
    if f_cell > 0:
        return f_cell - 1
    return 0


def merge(f, map):
    return [
        [merge_cell(f[i][j], map.at(j, i))
         for j in range(map.width())]
        for i in range(map.height())]

def merge_cell(f_cell, map_cell):
    if map_cell == game.WALL:
        return DEFAULT_CELL
    elif map_cell == game.PILL:
        return 900
    elif map_cell == game.POWER_PILL:
        return 905
    elif map_cell == game.FRUIT:
        return 910
    else:
        return f_cell


def merge_ghosts(f, ghosts):
    f = copy.deepcopy(f)
    for ghost in ghosts:
        if ghost.vitality == game.STANDARD:
            f[ghost.y][ghost.x] = 0
        elif ghost.vitality == game.FRIGHT:
            f[ghost.y][ghost.x] = 905
    return f


def main():
    f = [
    [0, 0, 0],
    [0, 9, 0],
    [0, 0, 0],
    ]

    f = diffuse(f)

    for line in f:
        print line


if __name__ == '__main__':
    main()
