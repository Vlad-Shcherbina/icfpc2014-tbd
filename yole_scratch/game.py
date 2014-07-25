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


class Ghost:
    def __init__(self, map, index, ai, x, y):
        self.map = map
        self.index = index
        self.direction = DOWN
        self.ai = ai
        self.vitality = STANDARD
        self.x = x
        self.y = y


class Map:
    def __init__(self, lines, ghost_ais):
        self.ghosts = []
        self.lambdamen = []
        self.cells = []
        for y, line in enumerate(lines):
            line_cells = []
            for x, c in line:
                contents = MAP_TILES.index(c)
                if contents == LAMBDAMAN:
                    self.lambdamen.append(LambdaMan(x, y))
                    contents = EMPTY
                elif contents == GHOST:
                    index = len(self.ghosts)
                    ai = ghost_ais[len(self.ghosts) % len(ghost_ais)]
                    self.ghosts.append(Ghost(self, index, ai, x, y))
                    contents = EMPTY
                line_cells.append(contents)
            self.cells.append(line_cells)

    def at(self, x, y):
        for lman in self.lambdamen:
            if lman.x == x and lman.y == y:
                return LAMBDAMAN
        for ghost in self.ghosts:
            if ghost.x == x and ghost.y == y:
                return GHOST
        return self.cells[y][x]
