# python aghost.py ../data/ghosts/ared_scatter.py >../data/ghosts/ared_scatter.ghc

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

    mem.best_closest = 0
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

        def dist(x1, y1, x2, y2):
            if x1 > x2:
                mem.result = x1 - x2
            else:
                mem.result = x2 - x1
            if y1 > y2:
                mem.result += y1 - y2
            else:
                mem.result += y2 - y1
            join()
            return mem.result

        mem.dist = dist(mem.x1, mem.y1, mem.tx, mem.ty)

        if mem.vitality == game.FRIGHT:
            mem.dist = 255 - mem.dist

        mem.self_index = get_index()
        mem.other_index = 0
        mem.closest = 255
        while mem.other_index < 5:
            if mem.other_index == mem.self_index:
                mem.other_index += 1
                continue
            mem.other_vitality, _ = get_ghost_status(mem.other_index)
            if (mem.other_vitality == game.FRIGHT) != (mem.vitality == game.FRIGHT):
                mem.other_index += 1
                continue
            join()
            mem.other_x, mem.other_y = get_ghost_coords(mem.other_index)
            if mem.other_x == 0:
                break
            mem.other_index += 1

            mem.dist_to_other = dist(mem.x1, mem.y1, mem.other_x, mem.other_y)
            if mem.closest > mem.dist_to_other:
                mem.closest = mem.dist_to_other

        # if distance to lm is the same, prefer to stay apart from closest ghost
        if (mem.dist < mem.best_dist or
            mem.dist == mem.best_dist and mem.best_closest < mem.closest):
            mem.best_dist = mem.dist
            mem.best_closest = mem.closest
            set_dir(mem.d)

    join()
    inline('HLT')
