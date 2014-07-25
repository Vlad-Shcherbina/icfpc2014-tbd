import json
import logging
import os
import sys

sys.path.append('../production')
import game


logger = logging.getLogger(__name__)


class Result(object):
    __slots__ = [
        'map',  # path relative to data/maps
        'pacman_spec',
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
            pacman_spec=self.pacman_spec,
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

    assert not result.pacman_spec.startswith('interactive:')

    logger.info('match between {} and {} on {}'.format(
        result.pacman_spec, result.ghost_specs, result.map))
    map = game.Map(lines, result.ghost_specs, result.pacman_spec)
    while not map.game_over():
        map.step()

    result.score = map.lambdamen[0].score
    result.ticks = map.current_tick
    logger.info('score: {}, ticks: {}'.format(result.score, result.ticks))


def play_tournament(maps, lm_specs, ghost_team_specs):
    assert len(lm_specs) == 1, 'comparing multiple LMs is not implemented yet'
    results = []
    for map in maps:
        for lm_spec in lm_specs:
            for ghost_team in ghost_team_specs:
                result = Result()
                result.map = map
                result.pacman_spec = lm_spec
                result.ghost_specs = ghost_team
                play(result)
                results.append(result)
    return results


def save_results(results, filename):
    with open(filename, 'w') as fout:
        json.dump(map(Result.to_json, results), fout, indent=2)


def main():
    logging.basicConfig(level=logging.INFO)

    results = play_tournament(
        maps=[
            'default_map.txt',
            'gen/hz.txt',
        ],
        lm_specs=[
            'py:lm_ai.Oscillating(frequency=5)',
        ],
        ghost_team_specs=[
            ['py:GhostAI_Shortest', 'ghc:fickle.ghc'],
            ['ghc:miner.ghc'],
        ])

    save_results(results, '../data/some_results.json')


if __name__ == '__main__':
    main()
