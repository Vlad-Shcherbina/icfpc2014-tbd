def main(world, _ghosts):
    field = matrix_map(always_default, world[0])
    return ((999888777, field), step)


def step(state, world):
    return (state, 1)


def default():
    return (0, 0)

def always_default(x):
    return default()


def shift_up(mat):
    return list_append(mat[1:], list_map(always_default, mat[0]))


################################################


def fail_():
    # TODO, like assert False
    return 0


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
    def inc(x):
        return x + 1
    return list_map(inc, xs)


def matrix_map(f, mat):
    def line_map(line):
        return list_map(f, line)
    return list_map(line_map, mat)


def matrix_inc_for_test(mat):
    def inc(x):
        return x + 1
    return matrix_map(inc, mat)
