def is_junction(world, x, y):
    free_cells = 0
    if get_cell_at(world[0], x+1, y) == 0:
        pass
    else:
        free_cells = free_cells + 1
    if get_cell_at(world[0], x-1, y) == 0:
        pass
    else:
        free_cells = free_cells + 1
    if get_cell_at(world[0], x, y+1) == 0:
        pass
    else:
        free_cells = free_cells + 1
    if get_cell_at(world[0], x, y-1) == 0:
        pass
    else:
        free_cells = free_cells + 1
    if free_cells > 2:
        return 1
    else:
        return 0

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
