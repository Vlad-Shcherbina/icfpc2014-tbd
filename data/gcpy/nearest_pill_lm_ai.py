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
  return f(state, world)

# strategy_state := (seed, current_direction)
def strategy_state():
  return (42, 0)

def f(state, world):
  res = f_do(3, -1, state, world)
  print res
  return res
def f_do(direction, minus_one, state, world):
  print direction
  if 0 > direction:
    if minus_one == 5:
      return g(state, world)
    else:
      print state
      return (state, 3)
  else:
    return f_do(direction - 1, minus_one, state, world)

def g(state, _world): return (state, 1)
