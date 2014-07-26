def list_length(l):
    return list_length_rec(l, 0)

def list_length_rec(l, result):
    if int(l):
        return result
    else:
        return list_length_rec(l[1:], result+1)


