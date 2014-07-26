import os
import game


def load_map(relative_path, ghost_specs, lm_spec):
    with open(os.path.join('../data/maps', relative_path)) as fin:
        lines = [l.strip() for l in fin.read().splitlines() if l.strip()]
    return game.Map(lines, ghost_specs, lm_spec)
