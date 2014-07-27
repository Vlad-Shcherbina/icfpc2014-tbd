## Random Walk Lambda Man
##
## Directions:
### 0: top
### 1: right
### 2: bottom
### 3: left
import math
 
def main(world, _ghosts): 
  return (strategy_state(), step)
def step(state, world):
  return (update_state(state), deduce_direction(state, world))

# Random walk strategy state
def strategy_state():
  #returns (seed, last_direction, count)
  return (42, (0, 0))

def update_state(state):
  return update_state_with_last_direction(random_direction(state[0], state[1:][0]), state)
def update_state_with_last_direction(direction, state):
  print direction
  return (lcg_seed(state[0]), (direction, state[1][1]+1))

# Deduce direction based on oscillation parameter
def deduce_direction(state, _world):
  return 2

# x % y
def modulo(x, y):
  return ( x - ( y * (x / y) ) )

# randomness
def lcg_seed(seed):
  return (seed * 1664525 + 1013904223) % int(math.pow(2, 32))
def lcg_bits(seed):
  return abs(((seed * 10000) / 1000000))
def random_direction(seed, last):
  return new_random_direction(modulo(lcg_bits(seed), 4), last)
def new_random_direction(candidate, last):
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

sstate, _step = main(0, 0)
for i in range(0, 8097):
  sstate, _dir = step(sstate, 0)
