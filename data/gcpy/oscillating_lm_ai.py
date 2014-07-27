## Oscillating Lambda Man
##
## Directions:
### 0: top
### 1: right
### 2: bottom
### 3: left
 
def main(world, _ghosts): 
  return (strategy_state(), step)
def step(state, world):
  return (update_state(state), deduce_direction(state, world))

# Oscilation strategy state
def strategy_state():
  #returns (frequency, count)
  return (4, 0)

# Increase count in oscilation
def update_state(state):
  return (state[0], state[1:]+1)

# Deduce direction based on oscillation parameter
def deduce_direction(state, _world):
  # if self.cnt % (2 * self.frequency) < self.frequency:
  if state[0] > modulo(state[1:], (2 * state[0])):
    return 3
  else:
    return 1

# x % y
def modulo(x, y):
  return ( x - ( y * (x / y) ) )
