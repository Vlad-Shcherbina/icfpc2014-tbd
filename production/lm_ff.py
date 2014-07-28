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
        best = DEFAULT_CELL
        for dir in game.DIRECTIONS:
            nx = map.lambdaman.x + game.DELTA_X[dir]
            ny = map.lambdaman.y + game.DELTA_Y[dir]
            if better(self.f[ny][nx], best):
                best = self.f[ny][nx]
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


# Cell components:
#    (pills and other food, ghosts, fruit)
DEFAULT_CELL = (0, 0, 0)


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


def combine_cell(f1_cell, f2_cell):
    return tuple(max(e1, e2) for e1, e2 in zip(f1_cell, f2_cell))

def decrement_cell(f_cell):
    return tuple(max(e - 1, 0) for e in f_cell)


def merge(f, map):
    return [
        [merge_cell(f[i][j], map.at(j, i))
         for j in range(map.width())]
        for i in range(map.height())]


def merge_cell(f_cell, map_cell):
    if map_cell == game.WALL:
        return DEFAULT_CELL
    elif map_cell == game.PILL:
        return (max(900, f_cell[0]), f_cell[1], f_cell[2])
    elif map_cell == game.POWER_PILL:
        return (max(905, f_cell[0]), f_cell[1], f_cell[2])
    # elif map_cell == game.FRUIT:
    #     # TODO: use fruit component of a field
    #     # TODO: or even better, use expected fruit location even when
    #     # it's not on the map, and use careful distance-based timing in
    #     # better() function.
    #     return (max(910, f_cell[0]), f_cell[1], f_cell[2])
    else:
        return f_cell


def merge_ghosts(f, ghosts):
    f = copy.deepcopy(f)
    for ghost in ghosts:
        if ghost.vitality == game.STANDARD:
            # - note that ghost blocks propagation of other fields
            # - it might be nice to know that there is ghost nearby
            #   (within, say, 5 cells)
            f[ghost.y][ghost.x] = (0, 2, 0)
        elif ghost.vitality == game.FRIGHT:
            cell = f[ghost.y][ghost.x]
            f[ghost.y][ghost.x] = (max(905, cell[0]), cell[1], cell[2])
        elif ghost.vitality == game.INVISIBLE:
            f[ghost.y][ghost.x] = (0, 1, 0)
        else:
            assert False
        # TODO: take invisible ghost into account (it's better than standard,
        # though worse than frightened)
    return f


def better(f_cell1, f_cell2):
    # TODO: take into account ghost and fruit components
    return f_cell1[0] - 100 * f_cell1[1] > f_cell2[0] - 100 * f_cell2[1]


def main():
    f = [
    [(0, 0, 0), (0, 0, 0), (0, 0, 0)],
    [(0, 0, 0), (9, 2, 1), (0, 0, 0)],
    [(0, 0, 0), (0, 0, 0), (0, 0, 0)],
    ]

    f = diffuse(f)

    for line in f:
        print line


if __name__ == '__main__':
    main()
