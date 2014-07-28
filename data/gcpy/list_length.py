from intrinsics import car, cdr, nil

def list_length(l):
    return list_length_rec(l, 0)

def list_length_rec(l, result):
    if nil(l):
        return result
    else:
        return list_length_rec(l[1:], result+1)

def list_length_fast(xs):
    res = 0
    while not nil(xs):
        xs = cdr(xs)
        res = res + 1
    return res


