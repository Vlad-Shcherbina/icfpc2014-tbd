UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

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

LAMBDAMAN_SPEED = 127
LAMBDAMAN_EATING_SPEED = 137

GHOST_SPEEDS = [130, 132, 134, 136]
GHOST_FRIGHT_SPEEDS = [195, 198, 201, 204]


class GhostAI:
    def __init__(self, code):
        self.code = code

    def run(self):
        # GHC INTERPRETER GOES HERE
        pass


class LambdaMan:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = LAMBDAMAN_SPEED

    def move(self):
        pass


class Ghost:
    def __init__(self, map, index, ai, ai_index, x, y):
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
        pass


class Map:
    def __init__(self, lines, ghost_ais):
        self.ghosts = []
        self.lambdamen = []
        self.cells = []
        self.current_tick = 0
        self.move_queue = []
        for y, line in enumerate(lines):
            line_cells = []
            for x, c in enumerate(line):
                contents = MAP_TILES.index(c)
                if contents == LAMBDAMAN:
                    lman = LambdaMan(x, y)
                    self.lambdamen.append(lman)
                    self.schedule(lman)
                elif contents == GHOST:
                    index = len(self.ghosts)
                    ai_index = len(self.ghosts) % len(ghost_ais)
                    ai = ghost_ais[ai_index]
                    ghost = Ghost(self, index, ai_index, ai, x, y)
                    self.ghosts.append(ghost)
                    self.schedule(ghost)
                line_cells.append(contents)
            self.cells.append(line_cells)

    def at(self, x, y):
        return self.cells[y][x]

    def schedule(self, actor):
        actor.next_move = self.current_tick + actor.speed
        i = 0
        while i < len(self.move_queue) and self.move_queue[i].next_move < actor.next_move:
            i += 1
        self.move_queue.insert(i, actor)

    def step(self):
        actor = self.move_queue.pop()
        self.current_tick = actor.next_move
        actor.move()
        self.schedule(actor)
