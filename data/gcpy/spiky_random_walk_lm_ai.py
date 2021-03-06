## Spiky Random Walk Lambda Man
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
  return step_do(state, deduce_direction(state, world))
def step_do(state, direction):
  return (update_state(state, direction), direction)

# Random walk strategy state
def strategy_state():
  #returns (seed, last_direction, count)
  return (42, (0, 0))

def update_state(state, direction):
  return (lcg_seed(state[0]), direction, state[2:]+1)

# Deduce direction based on oscillation parameter
def deduce_direction(state, _world):
  return random_direction(state[0], state[1:][0])

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
