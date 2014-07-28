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

def while_test1(x):
    res = 0
    while x > 0:
        res = res + 2
        x = x - 1
    return res

def while_test2(x):
    res = 0
    while x:
        res = res + 2
        x = x - 1
    return res

def while_test3(x):
    res = 0
    while not not x > 0:
        res = res + 2
        x = x - 1
    return res

