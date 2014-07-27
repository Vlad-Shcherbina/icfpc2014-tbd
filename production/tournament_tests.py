import tournament


def play_tournament_test():
    results = tournament.play_tournament(
        maps=[
            #'default_map.txt',
            'gen/hz.txt',
        ],
        lm_specs=[
            'py:lm_ai.Oscillating(frequency=5)',
        ],
        ghost_team_specs=[
            #['py:GhostAI_Shortest', 'ghc:fickle.ghc'],
            ['ghc:miner.ghc'],
        ])
    assert len(results) == 1


def test_gcc_file_spec():
    results = tournament.play_tournament(
        maps=[
            'gen/hz.txt',
        ],
        lm_specs=[
            'gcc_file:YoleGCC:../data/lms/right.gcc',
        ],
        ghost_team_specs=[
            ['ghc:miner.ghc'],
        ])
    assert len(results) == 1


def test_gcpy_file_spec():
    results = tournament.play_tournament(
        maps=[
            'gen/hz.txt',
        ],
        lm_specs=[
            'gcpy_file:YoleGCC:oscillating_lm_ai.py',
        ],
        ghost_team_specs=[
            ['ghc:miner.ghc'],
        ])
    assert len(results) == 1
