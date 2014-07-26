import os
import random
from random import randrange, shuffle
import sys

MAP_TILES = r"# .o%\="

def make_maze_map(w, h):
    visited = [[0] * w + [1] for _ in range(h)] + [[1] * (w + 1)]
    ver = [["# "] * w + ['#'] for _ in range(h)] + [[]]
    hor = [["##"] * w + ['#'] for _ in range(h + 1)]
 
    def walk(x, y):
        visited[y][x] = 1
        d = [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]
        shuffle(d)
        for (xx, yy) in d:
            if visited[yy][xx]: continue
            if xx == x: hor[max(y, yy)][x] = "# "
            if yy == y: ver[y][max(x, xx)] = "  "
            walk(xx, yy)
 
    walk(randrange(w), randrange(h))  
    
    map_hor = []
    map_ver = []
    for i in hor:
        result = []
        for j in i:
            result.append(list(j))
        map_hor.append(sum(result, []))
    #print map_hor
    #print ver
    for i in ver:
        result = []
        for j in i:
            result.append(list(j))
        map_ver.append(sum(result, []))
    #print map_ver
    
    maze = zip(map_hor, map_ver)
    #print maze
    map = [x for i in maze for x in i]        
    #for line in map:
    #   print ''.join(line)
    return map

def make_block_map(w, h, block_size):
    map = [['#'] * w for _ in range(h)]
    for i in range(1, h - 1):
        for j in range(1, w - 1):
            if i % block_size == 1 or j % block_size == 1:
                map[i][j] = ' '
    return map


def find_space(map, seed):
    rng = random.Random(seed)
    h = len(map) - 1
    w = len(map[0])

    assert any(' ' in line for line in map), "can't find space"

    while True:
        i = rng.randrange(h)
        j = rng.randrange(w)
        if map[i][j] == ' ':
            return i, j


def place(map, items_to_place, seed=42):
    for c in items_to_place:
        i, j = find_space(map, seed=seed)
        map[i][j] = c
        seed += 1474

def place_items(map, num_powerpills, num_ghosts, seed = 43):
    i, j = find_space(map, seed=seed)
    map[i][j] = '\\'
    for m in range(num_powerpills):
            i, j = find_space(map, seed=seed)
            map[i][j] = r'o'
            seed += 1474
    for m in range(num_ghosts):
            i, j = find_space(map, seed=seed)
            map[i][j] = r'='
            seed += 1474


def fill_with_pills(map, frac=0.5, seed=42):
    rng = random.Random(seed)
    for line in map:
        for i in range(len(line)):
            if line[i] == ' ' and rng.random() <= frac:
                line[i] = '.'


def save_map(map, filename):
    with open(os.path.join('../data/maps', filename), 'w') as fout:
        for line in map:
            for c in line:
                assert c in MAP_TILES
            print>>fout, ''.join(line)
            print ''.join(line)

def map_cleanup(map): #remove dead ends near border
    rows = len(map)
    cols = len(map[0])
    #print rows, cols
    for i in range(1, cols - 1):
        map[1][i] = ' '
        map[rows - 3][i] = ' '
    for i in range(1, rows - 2):
        map[i][1] = ' '
        map[i][cols - 2] = ' '

def create_map(w, h, powerpills, ghosts, pills_density):     
    map = make_maze_map(w, h)     
    map_cleanup(map)     
    place_items(map, powerpills, ghosts)     
    fill_with_pills(map, pills_density)     
    filename = 'map_' + str(w*2+1) + '_' + str(h*2+1) + '_' + str(powerpills) + '_' + str(ghosts) + '_' + str(pills_density) +'.txt'      
    save_map(map, filename)

def main():
    sys.setrecursionlimit(10000)
    create_map(w = 20, h = 20, powerpills = 20, ghosts = 10, pills_density = 0.6)


if __name__ == '__main__':
    main()
