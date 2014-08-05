# python aghost.py ../data/ghosts/ared.py >../data/ghosts/ared.ghc

import game

def run():
    WALL = 0
    EMPTY = 1
    PILL = 2
    POWER_PILL = 3
    FRUIT = 4
    LM_START = 5
    GHOST_START = 6

    mem.x, mem.y = get_ghost_coords(get_index())
    mem.tx, mem.ty = get_lm_coords()

    mem.vitality, mem.old_dir = get_ghost_status(get_index())

    mem.best_dist = 255

    mem.d = 4
    while mem.d:
        join()
        mem.d -= 1

        # can't turn around
        if mem.d ^ 2 == mem.old_dir:
            continue

        mem.x1 = mem.x
        mem.y1 = mem.y
        if mem.d == game.UP:
            mem.y1 -= 1
        elif mem.d == game.RIGHT:
            mem.x1 += 1
        elif mem.d == game.DOWN:
            mem.y1 += 1
        elif mem.d == game.LEFT:
            mem.x1 -= 1
        join()

        if get_map_square(mem.x1, mem.y1) == WALL:
            continue

        if mem.x1 > mem.tx:
            mem.dist = mem.x1 - mem.tx
        else:
            mem.dist = mem.tx - mem.x1

        if mem.y1 > mem.ty:
            mem.dist += mem.y1 - mem.ty
        else:
            mem.dist += mem.ty - mem.y1

        if mem.vitality == game.FRIGHT:
            mem.dist = 0 - mem.dist

        if mem.dist < mem.best_dist:
            mem.best_dist = mem.dist
            set_dir(mem.d)

    join()
    inline('HLT')
