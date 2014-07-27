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
  return new_seed_maybe_and_direction(state, world)

# strategy_state := (seed, current_direction)
def strategy_state():
  return (42, 0)

def new_seed_maybe_and_direction(state, world):
  return new_seed_maybe_and_direction_do(3,         (-1,           -1     ), state, world)
def new_seed_maybe_and_direction_do     (direction, best_score_and_best_dir, state, world):
  print direction
  print best_score_and_best_dir
  if 0 > direction:
    if best_score_and_best_dir[0] == -1:
      print 1
      return go_straight_maybe(state, world)
    else:
      print 0 #
      print 0 # Function works correctly and is about to return correct values
      print 0 # However its caller (new_seed_maybe_and_direction) never sees them :(
      print 0 #
      print state[0]
      print best_score_and_best_dir[1:]
      return (state[0], best_score_and_best_dir[1:])
  else:
    # Without no_tco_pls this call gets compiled out, made me pretty sad for good twenty seven minutes
    no_tco_pls = new_seed_maybe_and_direction_do(direction - 1, 
                                                 new_best_maybe(direction,
                                                                get_adjacent_cell(world, delta_x(direction), delta_y(direction)),
                                                                best_score_and_best_dir),
                                                 state,
                                                 world)
    return no_tco_pls

def new_best_maybe(direction, cell, best_score_and_best_dir):
  #pill_score       = 1 # TIL we have variables :D
  #power_pill_score = 2
  #fruit_score      = 2 # Several minutes later I've learned that they don't work
  if cell == 2:
    if 1 > best_score_and_best_dir[0]:
      return (1, direction)
    else:
      return best_score_and_best_dir
  else: 
    if cell == 3:
      if 2 > best_score_and_best_dir[0]:
        return (2, direction)
      else:
        return best_score_and_best_dir
    else: 
      if cell == 4:
        if 2 > best_score_and_best_dir[0]:
          return (2, direction)
        else:
          return best_score_and_best_dir
      else:
        return best_score_and_best_dir

def go_straight_maybe(state, world):
  return go_straight_maybe_do(delta_x(state[1:]), delta_y(state[1:]), state, world)

def go_straight_maybe_do(dx, dy, state, world):
  if(get_adjacent_cell(world, dx, dy) == 0):
    return (lcg_seed(state[0]), guaranteed_new_random_direction(state[0], state[1:]))
  else:
    return (state[0], state[1:])

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
  if direction == 0:       return  1
  else: 
    if direction == 1:     return  0
    else: 
      if direction == 2:   return -1
      else: 
        if direction == 3: return  0
        else:              return delta_y(abs(modulo(direction, 4)))

# x % y
def modulo(x, y):
  return ( x - ( y * (x / y) ) )

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

# relative lookup
def get_adjacent_cell(state, dx, dy):
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
