import sys
sys.path.append('../production')

import tournament
import game


def main():
    game.MAX_TICKS = 1e30
    [result] = tournament.play_tournament(
        #maps=['world-1.txt'],
        maps=['gen/stress64x64.txt'],
        lm_specs=[
            'gcpy_file:YoleGCC:ff.py',
            #'gcc_file:VorberGCC:../data/lms/right.gcc',
        ],
        ghost_team_specs=[
            ['ghosthon:../data/ghosts/redsplitt.ghy'],
        ],
        parallel=False)
    print result.score
    print result.gcc_stats


if __name__ == '__main__':
    main()
