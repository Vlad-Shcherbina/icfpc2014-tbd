def get_adjacent_cell(state, dx, dy):
    print dx
    return get_cell_at(state[0], state[1][1][0]+dx, state[1][1][1:]+dy)

def get_cell_at(map, x, y):
    if y == 0:
        return get_cell_at_col(map[0], x)
    else:
        return get_cell_at(map[1:], x, y-1)

def get_cell_at_col(map_row, x):
    if x == 0:
        return map_row[0]
    else:
        return get_cell_at_col(map_row[1:], x-1)
