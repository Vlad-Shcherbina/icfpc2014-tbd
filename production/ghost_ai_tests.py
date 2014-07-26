import tournament

def test_original_strategies():
    tournament.play_tournament(
        maps=[
            'default_map.txt',
        ],
        lm_specs=[
            'py:lm_ai.NearestPill()',
        ],
        ghost_team_specs=[
            ['py:GhostAI_Red', 'py:GhostAI_Pink'],
        ])
