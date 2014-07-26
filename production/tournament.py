import json
import logging
import os
import glob

import game


logger = logging.getLogger(__name__)


class Result(object):
    __slots__ = [
        'map',  # path relative to data/maps
        'lm_spec',
        'ghost_specs',  # list
        'score',
        'ticks',
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
            ticks=self.ticks)

    @staticmethod
    def from_json(data):
        result = Result()
        for k, v in data.items():
            setattr(result, k, v)
        return result


def play(result):
    'Take partially filled result, fill in game outcome.'
    with open(os.path.join('../data/maps', result.map)) as fin:
        lines = [line.strip('\n') for line in fin]

    assert not result.lm_spec.startswith('interactive:')

    logger.info('match between {} and {} on {}'.format(
        result.lm_spec, result.ghost_specs, result.map))
    map = game.Map(lines, result.ghost_specs, result.lm_spec)
    while not map.game_over():
        map.step()

    result.score = map.lambdaman.score
    result.ticks = map.current_tick
    logger.info('score: {}, ticks: {}'.format(result.score, result.ticks))


def play_tournament(maps, lm_specs, ghost_team_specs):
    results = []
    for map in maps:
        for lm_spec in lm_specs:
            for ghost_team in ghost_team_specs:
                result = Result()
                result.map = map
                result.lm_spec = lm_spec
                result.ghost_specs = ghost_team
                play(result)
                results.append(result)
    return results


def save_results(results, filename):
    with open(filename, 'w') as fout:
        json.dump(map(Result.to_json, results), fout, indent=2)


def all_maps():
    maps = []
    map_dir = '../data/maps'
    for dir, _, files in os.walk(map_dir):
        dir = os.path.relpath(dir, map_dir)
        for file in files:
            maps.append(os.path.join(dir, file))
    return maps


def main():
    logging.basicConfig(level=logging.INFO)
    results = play_tournament(
        # maps=[
        #     'default_map.txt',
        #     'gen/hz.txt',
        #     '../../twigil_scratch/map_91_91_100_10.txt',
        # ],
        maps=all_maps(),
        lm_specs=[
            'py:lm_ai.Oscillating(frequency=5)',
            'py:lm_ai.NearestPill()',
            'gcc_file:VorberGCC:../data/lms/right.gcc',
        ],
        ghost_team_specs=[
            ['py:GhostAI_Shortest', 'ghc:fickle.ghc'],
            ['ghc:miner.ghc'],
            ['py:GhostAI_Red', 'py:GhostAI_Pink'],
        ])

    save_results(results, '../data/some_results.json')


if __name__ == '__main__':
    main()
