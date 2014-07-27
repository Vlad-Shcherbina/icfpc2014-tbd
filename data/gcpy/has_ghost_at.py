def has_ghost_at(world, x, y):
    return has_ghost_from_list(world[2], x, y)

def has_ghost_from_list(ghost_list, x, y):
    if int(ghost_list):
        return 0
    else:
        ghost = ghost_list[0]
        ghost_coord = ghost[1]
        if ghost_coord[0] == x:
            if ghost_coord[1:] == y:
                return 1
            else:
                return has_ghost_from_list(ghost_list[1:], x, y)
        else:
            return has_ghost_from_list(ghost_list[1:], x, y)
