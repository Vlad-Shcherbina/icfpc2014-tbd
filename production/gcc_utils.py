def is_cons(gcc_expr):
    if isinstance(gcc_expr, tuple):
        assert len(gcc_expr) == 2
        return True
    else:
        return False


def tuple_to_gcc(tuple):
    """
    >>> tuple_to_gcc((1, 2, 3))
    (1, (2, 3))
    """
    assert len(tuple) >= 2, tuple
    x = tuple[-1]
    assert not is_cons(x), tuple
    for elem in tuple[-2::-1]:
        x = (elem, x)
    return x


def tuple_from_gcc(gcc_tuple):
    """
    >>> tuple_from_gcc((1, (2, 3)))
    (1, 2, 3)
    """
    result = []
    x = gcc_tuple
    while is_cons(x):
        elem, x = x
        result.append(elem)
    result.append(x)
    assert len(result) >= 2, gcc_tuple
    return tuple(result)


def list_to_gcc(list):
    """
    >>> list_to_gcc(range(3))
    (0, (1, (2, 0)))
    """
    x = 0
    for elem in reversed(list):
        x = (elem, x)
    return x


def list_from_gcc(gcc_list):
    """
    >>> list_from_gcc((0, (1, (2, 0))))
    [0, 1, 2]
    """
    result = []
    x = gcc_list
    while is_cons(x):
        elem, x = x
        result.append(elem)
    assert x == 0, gcc_list
    return result
