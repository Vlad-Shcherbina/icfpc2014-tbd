import os
import random

import game


def manhattan(w, h, block_size):
    map = [['#'] * w for _ in range(h)]
    for i in range(1, h - 1):
        for j in range(1, w - 1):
            if i % block_size == 1 or j % block_size == 1:
                map[i][j] = ' '
    return map


def find_space(map, seed):
    rng = random.Random(seed)
    h = len(map)
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


def fill_with_pills(map, frac=0.5, seed=42):
    rng = random.Random(seed)
    for line in map:
        for i in range(len(line)):
            if line[i] == ' ' and rng.random() <= frac:
                line[i] = '.'


def save_map(map, filename):
    with open(os.path.join('../data/maps/gen', filename), 'w') as fout:
        for line in map:
            for c in line:
                assert c in game.MAP_TILES
            print>>fout, ''.join(line)
            print ''.join(line)


def main():
    map = manhattan(21, 21, block_size=3)
    place(map, r'\oo==')
    fill_with_pills(map, 0.9)
    save_map(map, 'hz.txt')


if __name__ == '__main__':
    main()
