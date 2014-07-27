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

def test_hunter():
    tournament.play_tournament(
        maps=[
            'default_map.txt',
        ],
        lm_specs=[
            'py:lm_ai.NearestPill()',
            'py:lm_ai.NearestPill(straight=True)',
        ],
        ghost_team_specs=[
            ['py:Hunter'],
        ])

def test_splitters():
    tournament.play_tournament(
        maps=[
            'default_map.txt',
        ],
        lm_specs=[
            'py:lm_ai.NearestPill()',
            'py:lm_ai.NearestPill(straight=True)',
        ],
        ghost_team_specs=[
            ['py:Splitter'],
            ['py:RedSplitter']
        ])
