def find_cell(map, value):

    return find_in_col(map, value, 0)

def find_in_row(row, value,p):
    if int(row):
        return -1
    else:
        if row[0] == value:
            return p
        else:
            return find_in_row(row[1:], value, p+1)

def find_in_col(map, value, p):

    if int(map):
        return (-1,-1)
    else:
        if find_in_row(map[0], value, 0) > -1:
            return (find_in_row(map[0], value, 0), p)
        else:
            return find_in_col(map[1:], value, p+1)

    
    