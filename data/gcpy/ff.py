def main(world, _ghosts):
  return ((999888777, world[0]), step)


def step(state, world):
    return (state, 1)


################################################


def fail_():
    # TODO, like assert False
    return 0


### list utils

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
