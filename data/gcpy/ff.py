def main(world, _ghosts):
    field = matrix_map(always_default, world[0])
    # password for logging
    return ((999888777, field), step)


def step(state, world):
    old_field = state[1:]
    map = world[0]

    def propagate_field(f):
        f1 = diffuse(f)
        return matrix_map(merge_cell, matrix_zip(f1, map))

    # TODO: increase
    field = apply_n_times(propagate_field, 2, old_field)

    return ((state[0], field), 0)


def default():
    return (0, 0)

def always_default(x):
    return default()


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
        return (-1, 0)
    elif map_cell == 2:  # PILL
        return (max(f_cell[0], 900), 0)
    elif map_cell == 3:  # POWER_PILL
        return (max(f_cell[0], 905), 0)
    elif map_cell == 4:  # FRUIT
        return (max(f_cell[0], 910), 0)
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

def list_tail(xs):
    return xs[1:]

def list_length(xs):
    return list_length_rec(xs, 0)

def list_length_rec(xs, result):
    if int(xs):
        return result
    else:
        return list_length_rec(xs[1:], result + 1)


def list_append(xs, x):
    if int(xs):
        return (x, 0)
    else:
        return (xs[0], list_append(xs[1:], x))


def list_update(xs, idx, new_value):
    if int(xs):
        return fail_()
    else:
        if idx == 0:
            return (new_value, xs[1:])
        else:
            return (xs[0], list_update(xs[1:], idx - 1, new_value))


def list_at(xs, idx):
    if int(xs):
        return fail_()
    else:
        if idx == 0:
            return xs[0]
        else:
            return list_at(xs[1:], idx - 1)


def list_map(f, xs):
    if int(xs):
        return xs
    else:
        return (f(xs[0]), list_map(f, xs[1:]))


def list_inc_for_test(xs):
    return list_map(inc, xs)


def list_zip(xs, ys):
    if int(xs):
        return 0
    else:
        return ((xs[0], ys[0]), list_zip(xs[1:], ys[1:]))


def list_drop_last(xs):
    if int(xs):
        return fail_()
    else:
        t = xs[1:]
        if int(t):
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
