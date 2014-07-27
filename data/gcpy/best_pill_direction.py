def best_pill_direction(world):
    dir_and_score = find_best_pill_direction(world, 0, (0, 0))
    return dir_and_score[0]

def find_best_pill_direction(world, dir, best_dir_and_score):
    if dir == 4:
        return best_dir_and_score
    else:
        score_at_dir = get_score_for_direction(world, dir)
        if score_at_dir > best_dir_and_score[1:]:
            return find_best_pill_direction(world, dir+1, (dir, score_at_dir))
        else:
            return find_best_pill_direction(world, dir+1, best_dir_and_score)

def get_score_for_direction(world, dir):
    cell = get_adjacent_cell(world, delta_x(dir), delta_y(dir))
    if cell == 2:
        return 10
    else:
        if cell == 3:
            return 50
        else:
            return 0

def delta_x(dir):
    if dir == 0:
        return 0
    else:
        if dir == 1:
            return -1
        else:
            if dir == 2:
                return 0
            else:
                return 1

def delta_y(dir):
    if dir == 0:
        return -1
    else:
        if dir == 1:
            return 0
        else:
            if dir == 2:
                return 1
            else:
                return 0

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
