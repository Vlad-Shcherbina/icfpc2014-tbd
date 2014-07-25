import tournament

def play_tournament_test():
    results = tournament.play_tournament(
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
    assert len(results) == 4

