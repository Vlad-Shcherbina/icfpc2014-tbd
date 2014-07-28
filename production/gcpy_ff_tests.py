import tournament


def test_on_micro():
    [result] = tournament.play_tournament(
        maps=[
            'micro.txt',
        ],
        lm_specs=[
            'gcpy_file:YoleGCC:ff.py',
        ],
        ghost_team_specs=[
            ['py:GhostAI_Red', 'ghc:red.ghc'],
        ])
