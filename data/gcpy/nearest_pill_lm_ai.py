## Straight Nearest Pill Eating Lambda Man
## Never goes the same random direction twice in a row
##
## Directions:
### 0: top
### 1: right
### 2: bottom
### 3: left
 
def main(world, _ghosts): 
  return (strategy_state(), step)
def step(state, world):
  bd = best_pill_direction(world)
  if bd == -1:
    gothere = straight_maybe(state, world)
    return (gothere, gothere[1:])
  else:
    return (state, bd)

# strategy_state := (seed, current_direction)
def strategy_state():
  return (42, 0)

def straight_maybe(state, world):
  adj_cell = get_adjacent_cell(world, delta_x(state[1:]), delta_y(state[1:]))
  if adj_cell == 0:
    new_direction = random_direction(state[0], state[1:])
    new_seed = lcg_seed(state[0])
    return (new_seed, new_direction)
  else:
    return state

def best_pill_direction(world):
    dir_and_score = find_best_pill_direction(world, 3, (-1, -1))
    return dir_and_score[0]

def find_best_pill_direction(world, dir, best_dir_and_score):
  if dir == -1:
    return best_dir_and_score
  else:
    score_for_direction = get_score(world, delta_x(dir), delta_y(dir))
    if score_for_direction > best_dir_and_score[1:]:
      return find_best_pill_direction(world, dir-1, (dir, score_for_direction))
    else:
      return find_best_pill_direction(world, dir-1, best_dir_and_score)

def get_score(world, dx, dy):
  cell = get_adjacent_cell(world, dx, dy)
  if cell == 2:          return  1
  else:
    if cell == 3:        return  2
    else:
      if cell == 4:      return  2
      else:              return -1
  
def get_adjacent_cell(world, dx, dy):
    return get_cell_at(world[0], world[1][1][0]+dx, world[1][1][1:]+dy)

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

# deltas
def delta_x(direction):
  if direction == 0:       return  0
  else: 
    if direction == 1:     return  1
    else: 
      if direction == 2:   return  0
      else: 
        if direction == 3: return -1
        else:              return delta_x(abs(modulo(direction, 4)))

def delta_y(direction):
  if direction == 0:       return -1
  else: 
    if direction == 1:     return  0
    else: 
      if direction == 2:   return  1
      else: 
        if direction == 3: return  0
        else:              return delta_y(abs(modulo(direction, 4)))

# randomness
def lcg_seed(seed):
  return (seed * 1664525 + 1013904223)
def lcg_bits(seed):
  return abs(((seed * 10000) / 1000000))
def random_direction(seed, last):
  return guaranteed_new_random_direction(modulo(lcg_bits(seed), 4), last)
def guaranteed_new_random_direction(candidate, last):
  if candidate == last:
    return modulo(candidate + 1, 4)
  else:
    return candidate

# absolute value
def abs(x):
  if 0 > x:
    return -1 * x
  else:
    return x

# x % y
def modulo(x, y):
  return ( x - ( y * (x / y) ) )
