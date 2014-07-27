import ghosthon
import tournament


def test_basic():
    print ghosthon.full_compile("""
!myindex
!ghoststats
alias gdir [0]
alias gvit [6]
mov gdir, b
mov gvit, a

if a = b
    mov c, 1
else
    mov d, 0
!debug
    """)


def test_run():
    tournament.play_tournament(
        maps=[
            'default_map.txt',
        ],
        lm_specs=[
            'py:lm_ai.NearestPill()',
        ],
        ghost_team_specs=[
            ['ghosthon:../data/hello.ghy'],
        ])
