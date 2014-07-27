import os
import game


def load_map(relative_path):
    relative_path, _, rot = relative_path.partition('#')

    if rot:
        rot = int(rot)
    else:
        rot = 0

    with open(os.path.join('../data/maps', relative_path)) as fin:
        lines = [l.strip() for l in fin.read().splitlines() if l.strip()]

    h = len(lines)
    w = len(lines[0])
    assert all(len(line) == w for line in lines)

    for _ in range(rot):
        h = len(lines)
        w = len(lines[0])
        lines = [[lines[j][w - 1 - i] for j in range(h)] for i in range(w)]

    return game.Map(lines)
