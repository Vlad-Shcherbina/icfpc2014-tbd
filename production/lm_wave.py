import game
import random
import logging
import traceback
class Wavy(game.LambdaManAI):
    def __init__(self, depth):
        self.last_turn_pos = ()
        self.wave_depth = depth
        pass
    
    def get_move(self,world_map):
        #scores = map(lambda d: self.wave(world_map, d, self.wave_depth), range(4))
        #ms = max(scores)
        #dir = scores.index(ms)
        #self.last_turn_pos = (world_map.lambdaman.x, world_map.lambdaman.y)
        #return dir
        #print 'pos ', world_map.lambdaman.x, world_map.lambdaman.y
        dir = self.find_closest_safe_pill(world_map, self.wave_depth)
        return dir
        
    def wave(self,world_map,initial_direction, max_steps):
        '''
        Launches a wave into specified direction
        Returns a score for that direction
        Score computation is the most tricky part
        '''
        return self.unportable_wave(world_map, initial_direction, max_steps)
        
    
    def find_closest_safe_pill(self, world_map, max_steps):
        visited = map(lambda line:map(lambda cell:False if cell != game.WALL else True, line), world_map.cells)
        pos = (world_map.lambdaman.x, world_map.lambdaman.y)
        
        visited[world_map.lambdaman.y][world_map.lambdaman.x] = True
 
        neighbours = map(lambda d: self.apply_direction(d, pos[0], pos[1]), range(4))
        with_directions = zip(range(4), neighbours)

        wd_valid_neighbours = filter(lambda n: (not visited[n[1][1]][n[1][0]]) and self.fits(world_map, n[1][0],n[1][1]), with_directions)
        dir = 0 if len(wd_valid_neighbours) == 0 else wd_valid_neighbours[0]
        
        front = list(wd_valid_neighbours)
        step = 0
        ghost_positions = map(lambda g: (g.x, g.y), world_map.ghosts)
        ghost_directions = map(lambda g: g.direction, world_map.ghosts)
        ghosts_with_directions = zip(ghost_directions, ghost_positions)
        ghost_vit = map(lambda g: g.vitality, world_map.ghosts)
        next_ghost_positions = map(lambda gdp: self.apply_direction(gdp[0],gdp[1][0],gdp[1][1]), ghosts_with_directions)
        while step < max_steps:
            step += 1
            #print step
            #print front
            step_score = 0
            new_front = []
            while len(front)>0:
                (dir, (x,y)) = front.pop()
                #print 'analyzing ', (dir, (x,y))
                if (x,y) in ghost_positions or (x,y) in next_ghost_positions:
                    if world_map.fright_end > (step-1)*world_map.lambdaman.speed:
                        idx = (ghost_positions + next_ghost_positions).index((x,y)) % len(ghost_positions)
                        if ghost_vit[idx] != game.INVISIBLE:#don't chase invisible ones
                            return dir
                        #no else, treat invisible ghosts as empty square
                    else:
                        visited[y][x] = True
                        continue
                v = world_map.at(x,y) 
                if v == game.PILL or v == game.FRUIT or v == game.POWER_PILL:
                    return dir
                visited[y][x] = True
                neighbours = map(lambda d: self.apply_direction(d, x, y), range(4))
                #print 'neighbours', neighbours, map(lambda n: visited[n[1]][n[0]], neighbours), map(lambda n: world_map.at(n[0],n[1]), neighbours)
                wd = zip([dir]*4, neighbours) #maintain original direction
                valid = filter(lambda r: (not visited[r[1][1]][r[1][0]]) and self.fits(world_map, r[1][0],r[1][1]), wd)
                new_front+=list(valid)
            front = new_front
        #print 'no pills found!'
        return dir
        
    def unportable_wave(self,world_map, initial_direction, max_steps):
        nx,ny = self.apply_direction(initial_direction, world_map.lambdaman.x, world_map.lambdaman.y)
        if (not self.fits(world_map, nx, ny)) or world_map.at(nx,ny) == game.WALL:
            return -1000000
        visited = map(lambda line:map(lambda cell:False if cell != game.WALL else True, line), world_map.cells)
        visited[world_map.lambdaman.y][world_map.lambdaman.x] = True
        cell_score = self.visit(world_map, nx, ny)

        visited[ny][nx] = True
        dir_score = cell_score
        front = [(nx,ny)]
        step = 1
        while step < max_steps:
            step += 1

            step_score = 0
            new_front = []
            while len(front)>0:

                sx,sy = front.pop()
                for new_dir in range(4):

                    nx,ny = self.apply_direction(new_dir, sx,sy)

                    if (not self.fits(world_map, nx,ny)) or visited[ny][nx]:
                        pass
                    else:
                        substep_score = self.visit(world_map, nx, ny)
                        if (nx,ny) == self.last_turn_pos:
                            substep_score -= 100
                        step_score+=substep_score
                        visited[ny][nx] = True
                        new_front.append((nx,ny))

            front = new_front
            dir_score += step_score - step*1 #TODO: proper weighting for step
        return dir_score
        
    def visit(self, world_map, nx,ny):
        if self.fits(world_map, nx, ny):
            c = world_map.at(nx,ny)
            if c == game.PILL:#TODO: proper weights
                return 10
            elif c == game.POWER_PILL:
                return 100
            elif c == game.FRUIT:
                return 1000
            elif c == game.GHOST:
                #TODO: check for frightened/not frightened, duration and speed
                return -10
            elif c == game.WALL:
                #TODO: check for frightened/not frightened, duration and speed
                return -1000000
            else:
                return 1
        else:
            return 0
        
    def apply_direction(self, direction, x, y):
        if direction == 0:
            return (x, y-1)
        elif direction == 1:
            return (x+1,y)
        elif direction == 2:
            return (x,y+1)
        elif direction == 3:
            return (x-1,y)  
            
    def fits(self, world_map, x, y):
        return (x>=0) and (y>=0) and (world_map.width() > x ) and (world_map.height() > y)
        
    def wave_rec(self, world_map, visited):
        pass