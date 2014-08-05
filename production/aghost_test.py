import sys

import nose
from nose.tools import eq_

import tournament


def test_run():
    tournament.play_tournament(
        maps=[
            'map_15_19_4_4.txt',
        ],
        lm_specs=[
            'py:lm_ai.NearestPill()',
        ],
        ghost_team_specs=[
            ['aghost:../data/ghosts/ared.py'],
        ])


if __name__ == '__main__':
    nose.run_exit(argv=[
        sys.argv[0], __file__,
        '--verbose', '--with-doctest', '--logging-level=DEBUG'
    ])
