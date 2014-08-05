# python aghost.py ../data/ghosts/ared.py >../data/ghosts/ared.ghc

def run():
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

    mem.x, mem.y = get_ghost_coords(get_index())
    tx, ty = get_lm_coords()
    mem.dx = tx - mem.x
    mem.dy = ty - mem.y

    def abs(x):
        return x if x < 128 else 0 - x
    mem.adx = abs(mem.dx)
    mem.ady = abs(mem.dy)

    if mem.adx > mem.ady:
        if mem.dx < 128:
            set_dir(RIGHT)
        else:
            set_dir(LEFT)
    else:
        if mem.dy < 128:
            set_dir(DOWN)
        else:
            set_dir(UP)

    inline('HLT')
