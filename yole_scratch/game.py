UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3
OPPOSITE_DIRECTIONS = [DOWN, LEFT, UP, RIGHT]
DELTA_X = [0, 1, 0, -1]
DELTA_Y = [-1, 0, 1, 0]

STANDARD = 0
FRIGHT = 1
INVISIBLE = 2

WALL = 0
EMPTY = 1
PILL = 2
POWER_PILL = 3
FRUIT = 4
LAMBDAMAN = 5
GHOST = 6

MAP_TILES = r"# .o%\="

# Map tiles to display in the UI (don't show start location of pacman and ghosts)
MAP_TILES_VIEW = r"# .o%  "

LAMBDAMAN_SPEED = 127
LAMBDAMAN_EATING_SPEED = 137

GHOST_SPEEDS = [130, 132, 134, 136]
GHOST_FRIGHT_SPEEDS = [195, 198, 201, 204]

FRUIT_SPAWN_TIMES = [127*200, 127*400]

PILL_SCORE = 10
POWER_PILL_SCORE = 50
GHOSTS_EATEN_SCORES = [200, 400, 800, 1600]
FRUIT_SCORES = [100, 300, 500, 500, 700, 700, 1000, 1000, 2000, 2000, 3000, 3000]

FRIGHT_DURATION = 127 * 20

class GhostAI:
    def __init__(self, map, code):
        self.map = map
        self.code = code

    def get_move(self):
        # GHC INTERPRETER GOES HERE
        return DOWN


class LambdaManAI(object):
    def get_move(self):
        raise NotImplementedError()


class InteractiveLambdaManAI(LambdaManAI):
    def __init__(self):
        self.direction = None

    def get_move(self):
        return self.direction


class Actor(object):
    def __init__(self, map, x, y):
        self.map = map
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y

    def move_in_direction(self, direction):
        new_x = self.x + DELTA_X[direction]
        new_y = self.y + DELTA_Y[direction]
        if self.map.at(new_x, new_y) != WALL:
            self.x = new_x
            self.y = new_y
            return True
        return False


class LambdaMan(Actor):
    def __init__(self, map, x, y, ai):
        super(LambdaMan, self).__init__(map, x, y)
        self.speed = LAMBDAMAN_SPEED
        self.score = 0
        self.lives = 3
        self.ai = ai

    def move(self):
        direction = self.ai.get_move()
        self.move_in_direction(direction)
        self.check_collisions()

    def check_collisions(self):
        c = self.map.at(self.x, self.y)
        if c == PILL:
            self.eat(PILL_SCORE)
        elif c == POWER_PILL:
            self.eat(POWER_PILL_SCORE)
            self.map.frighten_ghosts()
        elif c == FRUIT:
            self.eat(self.map.fruit_score())
        else:
            self.speed = LAMBDAMAN_SPEED

    def eat(self, score):
        self.map.clear(self.x, self.y)
        self.score += score
        self.speed = LAMBDAMAN_EATING_SPEED

    def eaten(self):
        self.lives -= 1
        self.reset()


class Ghost(Actor):
    def __init__(self, map, index, ai_index, ai, x, y):
        super(Ghost, self).__init__(map, x, y)
        self.map = map
        self.index = index
        self.direction = DOWN
        self.ai = ai
        self.ai_index = ai_index
        self.vitality = STANDARD
        self.x = x
        self.y = y
        self.speed = GHOST_SPEEDS[self.ai_index]

    def move(self):
        new_dir = self.ai.get_move()
        self.move_in_direction(new_dir)

    def frighten(self):
        self.vitality = FRIGHT
        self.direction = OPPOSITE_DIRECTIONS[self.direction]

    def eaten(self):
        self.vitality = INVISIBLE
        self.direction = DOWN
        self.reset()


class FruitSpawnpoint(Actor):
    def __init__(self, map, x, y, index):
        super(FruitSpawnpoint, self).__init__(map, x, y)
        self.speed = FRUIT_SPAWN_TIMES[index]

    def move(self):
        pass


class Map:
    def __init__(self, lines, ghost_ghc_codes, lman_ai):
        self.ghosts = []
        self.lambdamen = []
        self.cells = []
        self.current_tick = 0
        self.move_queue = []
        self.pills_remaining = 0
        self.ghosts_eaten = 0
        self.fruits = 0
        self.fright_end = None
        for y, line in enumerate(lines):
            line_cells = []
            for x, c in enumerate(line):
                contents = MAP_TILES.index(c)
                if contents == LAMBDAMAN:
                    lman = LambdaMan(self, x, y, lman_ai)
                    self.lambdamen.append(lman)
                    self.schedule(lman)
                elif contents == GHOST:
                    index = len(self.ghosts)
                    ai_index = len(self.ghosts) % len(ghost_ghc_codes)
                    ai = GhostAI(self, ghost_ghc_codes[ai_index])
                    ghost = Ghost(self, index, ai_index, ai, x, y)
                    self.ghosts.append(ghost)
                    self.schedule(ghost)
                elif contents == PILL:
                    self.pills_remaining += 1
                elif contents == FRUIT:
                    spawnpoint = FruitSpawnpoint(map, x, y, self.fruits)
                    self.fruits += 1
                    self.schedule(spawnpoint)
                    contents = EMPTY
                line_cells.append(contents)
            self.cells.append(line_cells)

    def width(self):
        return len(self.cells[0])

    def height(self):
        return len(self.cells)

    def at(self, x, y):
        return self.cells[y][x]

    def line_as_text(self, y):
        result = [MAP_TILES_VIEW[c] for c in self.cells[y]]
        for lman in self.lambdamen:
            if lman.y == y:
                result[lman.x] = '\\'
        for ghost in self.ghosts:
            if ghost.y == y:
                result[ghost.x] = '='
        return ''.join(result)

    def clear(self, x, y):
        c = self.at(x, y)
        if c == PILL:
            self.pills_remaining -= 1
        self.cells[y][x] = EMPTY

    def schedule(self, actor):
        actor.next_move = self.current_tick + actor.speed
        i = 0
        while i < len(self.move_queue) and self.move_queue[i].next_move < actor.next_move:
            i += 1
        self.move_queue.insert(i, actor)

    def step(self):
        actor = self.move_queue[0]
        del self.move_queue[0]
        self.current_tick = actor.next_move
        if self.fright_end and self.current_tick >= self.fright_end:
            self.unfrighten_ghosts()
        actor.move()
        self.check_lman_ghost_collisions()
        self.schedule(actor)

    def frighten_ghosts(self):
        for ghost in self.ghosts:
            ghost.frighten()
        self.ghosts_eaten = 0
        self.fright_end = self.current_tick + FRIGHT_DURATION

    def unfrighten_ghosts(self):
        for ghost in self.ghosts:
            ghost.vitality = STANDARD
        self.fright_end = None

    def reset_ghosts(self):
        for ghost in self.ghosts:
            ghost.reset()

    def fruit_score(self):
        l = self.level()
        if l >= len(FRUIT_SCORES):
            return FRUIT_SCORES[-1]
        return FRUIT_SCORES[l]

    def level(self):
        return len(self.cells) * len(self.cells[0]) / 100

    def check_lman_ghost_collisions(self):
        for lman in self.lambdamen:
            for ghost in self.ghosts:
                if lman.x == ghost.x and lman.y == ghost.y:
                    if ghost.vitality == FRIGHT:
                        ghost.eaten()
                        lman.score += self.ghost_eaten_score()
                        self.ghosts_eaten += 1
                    elif ghost.vitality == STANDARD:
                        lman.eaten()
                        self.reset_ghosts()

    def ghost_eaten_score(self):
        if self.ghosts_eaten >= len(GHOSTS_EATEN_SCORES):
            return GHOSTS_EATEN_SCORES[-1]
        return GHOSTS_EATEN_SCORES[self.ghosts_eaten]

    def game_over(self):
        if self.pills_remaining == 0:
            return True
        if all([lman.lives == 0 for lman in self.lambdamen]):
            return True
        return False
