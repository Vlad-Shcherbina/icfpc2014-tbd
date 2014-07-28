def to_int32(x):
    # this is guaranteed to fit into int on 32bit machines
    return int((x & 0xFFFFFFFF) - ((x & 0x80000000) << 1))


def deep_marshal(gcc, x):
    if type(x) == tuple:
        a, b = x
        x = (deep_marshal(gcc, a), deep_marshal(gcc, b))
        return gcc.marshal(x)
    elif isinstance(x, (int, long)):
        return gcc.marshal(x)
    else:
        return x


def deep_unmarshal(gcc, x):
    x = gcc.unmarshal(x)
    if type(x) == tuple:
        a, b = x
        x = (deep_unmarshal(gcc, a), deep_unmarshal(gcc, b))
        return x
    else:
        return x


def lto_to_cons(x, marshal=lambda x: x):
    '''Convert a recursive list/tuple/object structure to cons representation.
    If marshal is specified (should be gcc.marshal), everything is marshalled automatically,
    which is more efficient than calling deep_marshal on the result.
    Lists and tuples must be exact types, everything else is considered to be an "object"
    '''

    if type(x) == tuple:
        curr = None
    elif type(x) == list:
        curr = marshal(0)
    else:
        return marshal(x)

    for it in reversed(x):
        it = lto_to_cons(it, marshal)
        if curr is None:
            curr = it
        else:
            curr = marshal((it, curr))
    return curr


def cons_to_tuple(x, length):
    '''
    >>> cons_to_tuple((1, (2, 3)), 3)
    (1, 2, 3)
    '''
    assert length >= 1
    result = []
    for _ in xrange(length - 1):
        elem, x = x
        result.append(elem)
    result.append(x)
    return tuple(result)


def cons_to_list(x):
    '''
    >>> cons_to_list((1, (2, (3, 0))))
    [1, 2, 3]
    '''
    result = []
    while x != 0:
        elem, x = x
        result.append(elem)
    return result


def is_cons(x):
    return type(x) == tuple


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
