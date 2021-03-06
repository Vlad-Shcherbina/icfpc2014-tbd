import json
import logging
import os
import glob
import multiprocessing
import copy
import itertools

import game
import map_loader


logger = logging.getLogger(__name__)


class Result(object):
    __slots__ = [
        'map',  # path relative to data/maps
        'lm_spec',
        'ghost_specs',  # list
        'score',
        'ticks',
        'fruits_eaten',
        'ghosts_eaten',
        'power_pills_eaten',
        'gcc_stats',
    ]
    # For now pacman and ghost specs representation is not defined.
    # Let's assume they are json-able objects, strings maybe.

    # Another possible extension would be to keep count of game events
    # (how many lifes lost, how many ghosts, powerpills and fruits eaten)

    def to_json(self):
        return dict(
            map=self.map,
            lm_spec=self.lm_spec,
            ghost_specs=self.ghost_specs,
            score=self.score,
            ticks=self.ticks,
            fruits_eaten=self.fruits_eaten,
            ghosts_eaten=self.ghosts_eaten,
            power_pills_eaten=self.power_pills_eaten,
            gcc_stats=self.gcc_stats,
            )

    def baseline_score(self):
        """Just some number to scale actual score against."""
        # TODO: cache
        with open(os.path.join('../data/maps', self.map).partition('#')[0]) as fin:
            data = fin.read().strip()
        x = game.PILL_SCORE * data.count('.') + 1.0
        x += game.POWER_PILL_SCORE * data.count('o')
        # This score is imprecise, we don't care.
        assert x > 0
        return x

    @staticmethod
    def from_json(data):
        result = Result()
        for k, v in data.items():
            setattr(result, k, v)
        result.gcc_stats = game.GccStats(*result.gcc_stats)
        return result


def play(result):
    result = copy.copy(result)
    'Take partially filled result, fill in game outcome.'
    map = map_loader.load_map(result.map)
    map.set_ai_specs(result.lm_spec, result.ghost_specs)

    assert not result.lm_spec.startswith('interactive:')

    logger.info('match between {} and {} on {}'.format(
        result.lm_spec, result.ghost_specs, result.map))
    while not map.game_over():
        map.step()

    result.score = map.get_final_score()
    result.ticks = map.current_tick
    result.fruits_eaten = map.fruits_eaten
    result.power_pills_eaten = map.power_pills_eaten
    result.ghosts_eaten = map.ghosts_eaten
    result.gcc_stats = map.lman_vm_statistics()
    logger.info('score: {}, ticks: {}'.format(result.score, result.ticks))
    return result


def play_tournament(maps, lm_specs, ghost_team_specs, parallel=False):
    results = []
    for m in maps:
        for lm_spec in lm_specs:
            for ghost_team in ghost_team_specs:
                result = Result()
                result.map = m
                result.lm_spec = lm_spec
                result.ghost_specs = ghost_team
                results.append(result)

    if parallel:
        results_generator = multiprocessing.Pool().imap_unordered(play, results)
    else:
        results_generator = itertools.imap(play, results)

    rs = []
    for i, result in enumerate(results_generator):
        logger.warning('{}/{}, {}%'.format(i, len(results), 100 * i // len(results)))
        rs.append(result)

    return rs


def save_results(results, filename):
    with open(filename, 'w') as fout:
        json.dump(map(Result.to_json, results), fout, indent=2)


def all_maps(max_size=1000000):
    maps = []
    map_dir = '../data/maps'
    for dir, _, files in os.walk(map_dir):
        rel_dir = os.path.relpath(dir, map_dir)
        for file in files:
            with open(os.path.join(dir, file)) as fin:
                if len(fin.read().strip()) > max_size:
                    continue
            maps.append(os.path.join(rel_dir, file))
    return maps

def all_rotations(maps):
    return ['{}#{}'.format(m, rot) for m in maps for rot in range(4)]

def main():
    logging.basicConfig(level=logging.WARNING)
    #logger.setLevel(logging.INFO)
    results = play_tournament(
        # maps=[
        #     'map_21_9_10_3_0.7.txt#2'
        #      'map_big_noghost.txt'
        #     'default_map.txt',
        #     'gen/hz.txt',
        #     '../../twigil_scratch/map_91_91_100_10.txt',
        #],
        maps=all_rotations(all_maps(max_size=2500)),
        #maps=all_maps(max_size=500),
        lm_specs=[
            #'py:lm_ai.Oscillating(frequency=5)',
            #'py:lm_ai.NearestPill()',
            #'gcc_file:YoleGCC:../data/lms/right.gcc',
            #'py:lm_ai.NearestPill(straight=True)',
            'py:lm_ai.TunnelDigger()',
            'py:lm_wave.Wavy(50)',
            'py:lm_ff.ForceField()',
            'gcpy_file:YoleGCC:ff.py',
            #'gcc_file:VorberGCC:../data/lms/right.gcc',
        ],
        ghost_team_specs=[
            #['py:GhostAI_Random', 'ghc:miner.ghc', 'ghc:fickle.ghc', 'ghc:flipper.ghc'],  # degenerate scum
            #['py:GhostAI_Shortest'],
            #['py:GhostAI_Red', 'py:GhostAI_Pink'],
            #['py:GhostAI_Red'],
            ['ghosthon:../data/ghosts/red.ghy'],
            ['ghosthon:../data/ghosts/redsplitt.ghy'],
            #['ghc:red.ghc'],
            #['py:Hunter'],
        ],
        parallel=True)

    save_results(results, '../data/some_results.json')


if __name__ == '__main__':
    main()
