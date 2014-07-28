import tournament


def test_no_ghosts():
    [result] = tournament.play_tournament(
        maps=[
            'labyrinth_no_ghosts.txt',
        ],
        lm_specs=[
            'py:lm_ff.ForceField()',
        ],
        ghost_team_specs=[
            ['py:GhostAI_Red', 'ghc:red.ghc'],
        ])
    assert result.score > 1000, result.score


def test_some_map():
    [result] = tournament.play_tournament(
        maps=[
            'map_15_19_4_4.txt',
        ],
        lm_specs=[
            'py:lm_ff.ForceField()',
        ],
        ghost_team_specs=[
            ['py:GhostAI_Red', 'ghc:red.ghc'],
        ])
    assert result.score > 250, result.score
