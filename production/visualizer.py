"""
Examples:
    visualizer.py
    visualizer.py --map=gen/hz.txt --lm="py:lm_ai.Oscillating(frequency=5)" ghc:fickle.ghc ghc:miner.ghc
"""

import random
import curses
import logging
import argparse
import os
import sys

from game import GhostAI, Map, LambdaMan
from game import InteractiveLambdaManAI, set_interactive_lambda_man_direction


DIRECTION_KEYS = [
    curses.KEY_UP, curses.KEY_RIGHT, curses.KEY_DOWN, curses.KEY_LEFT]


def main():
    logging.basicConfig(level=logging.DEBUG, filename='visualizer_debug.log')

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--map', default='default_map.txt',
        help='map file, relative to data/maps')
    parser.add_argument('--lm', default='interactive:', help='lm spec')
    parser.add_argument('ghost', nargs='*', help='ghost specs')

    args = parser.parse_args()
    print args
    if not args.ghost:
        args.ghost = [
            'py:GhostAI_Shortest',
            'ghc:fickle.ghc',
        ]
        print 'no ghosts specified, using', args.ghost

    assert args.lm == 'interactive:', 'lm AIs not supported yet'

    with open(os.path.join('../data/maps', args.map)) as fin:
        lines = [line.strip('\n') for line in fin]

    map = Map(lines, args.ghost, args.lm)

    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(1)

    try:
        while True:
            if map.game_over():
                break
            for y in range(map.height()):
                stdscr.addstr(y, 0, map.line_as_text(y))
            stdscr.addstr(map.height(), 0, "Tick {0} Score {1}".format(
                map.move_queue[0].next_move, map.lambdamen[0].score))
            stdscr.refresh()
            next_actor = map.move_queue[0]
            if isinstance(next_actor, LambdaMan):
                quit_game = False
                while True:
                    c = stdscr.getch()
                    if c in (27,   # ESC
                             113,  # 'q'
                            ):
                        quit_game = True
                        break
                    if c in DIRECTION_KEYS:
                        set_interactive_lambda_man_direction(
                            DIRECTION_KEYS.index(c))
                        break
                    stdscr.addstr(map.height()+1, 0, "Unknown key {}".format(c))
                    stdscr.refresh()
                if quit_game:
                    break
            map.step()
    finally:
        curses.nocbreak()
        stdscr.keypad(0)
        curses.echo()
        curses.endwin()
        print "Tick {0} Score {1}".format(map.current_tick,
                                          map.lambdamen[0].score)


if __name__ == '__main__':
    main()
