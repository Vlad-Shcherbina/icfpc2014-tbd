# python gcpy.py -p ff.py -c -o ../data/lms/ff.gcc

from intrinsics import car, cdr, nil

def main(world, _ghosts):
    field = matrix_map(always_default, world[0])
    # password for logging
    return (999888777, field), step


def step(state, world):
    old_field = state[1:]
    map = world[0]
    me = world[1]
    ghosts = world[2]

    def propagate_field(f):
        f1 = diffuse(f)
        f2 = matrix_map(merge_cell, matrix_zip(f1, map))

        def apply_ghost(ff, ghost):
            vitality = ghost[0]
            coords = ghost[1]
            ghost_x = coords[0]
            ghost_y = coords[1:]
            old_cell = matrix_at(ff, ghost_x, ghost_y)
            if vitality == 1:  # fright mode
                new_cell = (max(old_cell[0], 905), 0)
            else:
                new_cell = default()
            return matrix_update(ff, ghost_x, ghost_y, new_cell)

        f3 = list_fold(apply_ghost, f2, ghosts)

        return f3

    field = apply_n_times(propagate_field, 10, old_field)

    my_coords = me[1]
    my_x = my_coords[0]
    my_y = my_coords[1:]

    candidate0 = \
        (0, matrix_at(field, my_x, my_y - 1))
    candidates = (
        (1, matrix_at(field, my_x + 1, my_y)),
        (2, matrix_at(field, my_x, my_y + 1)),
        (3, matrix_at(field, my_x - 1, my_y)),
        0)
    def pick_best(c1, c2):
        if better(c1[1:], c2[1:]):
            return c1
        else:
            return c2
    best = list_fold(pick_best, candidate0, candidates)

    return (state[0], field), best[0]
    #return ghosts[0], 0


def default():
    return (0, 0)

def always_default(x):
    return default()


def better(f_cell1, f_cell2):
    return f_cell1[0] > f_cell2[0]


def shift_up(mat):
    return list_append(mat[1:], list_map(always_default, mat[0]))

def shift_down(mat):
    return (list_map(always_default, mat[0]), list_drop_last(mat))

def shift_left(mat):
    def shift_row_left(xs):
        list_append(xs[1:], default())
    return list_map(shift_row_left, mat)

def shift_right(mat):
    def shift_row_right(xs):
        return (default(), list_drop_last(xs))
    return list_map(shift_row_right, mat)


def merge_cell(pair):
    f_cell = pair[0]
    map_cell = pair[1:]
    if map_cell == 0:  # WALL
        return (0, 0)
    elif map_cell == 2:  # PILL
        return (max(f_cell[0], 900), 0)
    elif map_cell == 3:  # POWER_PILL
        return (max(f_cell[0], 905), 0)
    # elif map_cell == 4:  # FRUIT
    #     return (max(f_cell[0], 910), 0)
    else:
        return f_cell


def decrement(field):
    def cell_dec(xs):
        def dec(x):
            if x == 0:
                return 0
            else:
                return x - 1
        return list_map(dec, xs)
    return matrix_map(cell_dec, field)


def combine(field1, field2):
    def cell_max(pair):
        xs = pair[0]
        ys = pair[1:]
        def max_of_pair(pair):
            x = pair[0]
            y = pair[1:]
            if x > y:
                return x
            else:
                return y
        return list_map(max_of_pair, list_zip(xs, ys))
    return matrix_map(cell_max, matrix_zip(field1, field2))


def diffuse(field):
    t = combine(shift_left(field), shift_up(field))
    t2 = shift_right(shift_down(t))
    return decrement(combine(t, t2))


################################################


def fail_():
    # TODO, like assert False
    return 0


def inc(x):
    return x + 1


def max(x, y):
    if x > y:
        return x
    else:
        return y


def apply_n_times(f, n, x):
    if n == 0:
        return x
    else:
        return apply_n_times(f, n - 1, f(x))


def inc_n_times_for_test(n, x):
    return apply_n_times(inc, n, x)


### list utils


def list_fold(f, initial, xs):
    if nil(xs):
        return initial
    else:
        return list_fold(f, f(initial, xs[0]), xs[1:])

def mk_pair(x, y):
    return (x, y)

def fold_mk_pair_for_test(initial, xs):
    return list_fold(mk_pair, initial, xs)


def list_tail(xs):
    return xs[1:]

def list_length(xs):
    return list_length_rec(xs, 0)

def list_length_rec(xs, result):
    if nil(xs):
        return result
    else:
        return list_length_rec(xs[1:], result + 1)


def list_append(xs, x):
    if nil(xs):
        return (x, 0)
    else:
        return (xs[0], list_append(xs[1:], x))


def list_update(xs, idx, new_value):
    if nil(xs):
        return fail_()
    else:
        if idx == 0:
            return (new_value, xs[1:])
        else:
            return (xs[0], list_update(xs[1:], idx - 1, new_value))


def list_at(xs, idx):
    if nil(xs):
        return fail_()
    else:
        if idx == 0:
            return xs[0]
        else:
            return list_at(xs[1:], idx - 1)


def list_map(f, xs):
    if nil(xs):
        return xs
    else:
        return (f(xs[0]), list_map(f, xs[1:]))


def list_inc_for_test(xs):
    return list_map(inc, xs)


def list_zip(xs, ys):
    if nil(xs):
        return 0
    else:
        return (xs[0], ys[0]), list_zip(xs[1:], ys[1:])


def list_drop_last(xs):
    if nil(xs):
        return fail_()
    else:
        t = xs[1:]
        if nil(t):
            return 0
        else:
            return (xs[0], list_drop_last(t))


# matrix utils

def matrix_at(mat, x, y):
    return list_at(list_at(mat, y), x)


def matrix_map(f, mat):
    def line_map(line):
        return list_map(f, line)
    return list_map(line_map, mat)


def matrix_inc_for_test(mat):
    return matrix_map(inc, mat)


def matrix_update(mat, x, y, new_value):
    list_update(mat, y, list_update(list_at(mat, y), x, new_value))


def matrix_zip(mat1, mat2):
    def lines_zip(line_pair):
        line1 = line_pair[0]
        line2 = line_pair[1:]
        return list_zip(line1, line2)
    return list_map(lines_zip, list_zip(mat1, mat2))
