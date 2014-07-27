def fail_():
    # TODO, like assert False
    return 0


def list_length(l):
    return list_length_rec(l, 0)

def list_length_rec(l, result):
    if int(l):
        return result
    else:
        return list_length_rec(l[1:], result+1)


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
