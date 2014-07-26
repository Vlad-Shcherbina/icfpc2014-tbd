"""
Examples:
    visualizer.py
    visualizer.py --map=gen/hz.txt --lm="py:lm_ai.Oscillating(frequency=5)" ghc:fickle.ghc ghc:miner.ghc

Controls:
   ESC, q - quit
   b - one step back
   arrows - control interactive lm
   any key - one step of non-interactive lm
"""

import random
import curses
import logging
import argparse
import os
import sys
import copy

import map_loader
import game
from game import GhostAI, Map, LambdaMan
from game import InteractiveLambdaManAI, set_interactive_lambda_man_direction
from log_context import log_context, decorate_handlers


MAX_HISTORY_SIZE = 100

DIRECTION_KEYS = [
    curses.KEY_UP, curses.KEY_RIGHT, curses.KEY_DOWN, curses.KEY_LEFT]


def main():
    # clear old log
    with open('visualizer_debug.log', 'w'):
        pass
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)8s:%(name)15s: %(message)s',
        filename='visualizer_debug.log')
    decorate_handlers()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--map', default='default_map.txt',
        help='map file, relative to data/maps')
    parser.add_argument('--lm', default='interactive:', help='lm spec')
    parser.add_argument('ghost', nargs='*', help='ghost specs')

    args = parser.parse_args()
    if not args.ghost:
        args.ghost = [
            'py:GhostAI_Shortest',
            'ghc:fickle.ghc',
        ]
        print 'no ghosts specified, using', args.ghost

    map = map_loader.load_map(args.map)
    map.set_ai_specs(args.lm, args.ghost)

    stdscr = curses.initscr()

    curses.noecho()
    curses.cbreak()
    stdscr.keypad(1)

    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)

    ghost_colors = [curses.color_pair(i) for i in 2, 3, 4, 5]

    try:
        history = []
        while not map.game_over():
            history = history[-MAX_HISTORY_SIZE:]
            for y in range(map.height()):
                stdscr.addstr(y, 0, map.line_as_text(y))
            for i, ghost in enumerate(map.ghosts):
                idx = ghost.index % len(args.ghost)
                if ghost.vitality != game.INVISIBLE:
                    stdscr.addstr(ghost.y, ghost.x, '=', ghost_colors[idx])
                stdscr.addstr(
                    i, map.width() + 1,
                    '{} {}'.format(ghost.vitality, args.ghost[idx]), ghost_colors[idx])

            #for i, ghost in enumerate(args.ghost):

            stdscr.addstr(
                5, map.width() + 1,
                'pill: {}    '.format(map.remaining_power_pill_ticks()),
                curses.color_pair(1))

            stdscr.addstr(map.height(), 0, "Tick {0} Score {1}   ".format(
                map.move_queue[0].next_move, map.lambdaman.score))
            stdscr.refresh()
            next_actor = map.move_queue[0]
            if isinstance(next_actor, LambdaMan):
                quit_game = False
                rewind = False
                if args.lm == 'interactive:':
                    while True:
                        c = stdscr.getch()
                        if c in (27, 113):  # ESC, q
                            quit_game = True
                            break
                        if c == ord('b'):
                            rewind = True
                            break
                        if c in DIRECTION_KEYS:
                            set_interactive_lambda_man_direction(
                                DIRECTION_KEYS.index(c))
                            break
                        stdscr.addstr(map.height()+1, 0, "Unknown key {}".format(c))
                        stdscr.refresh()
                else:
                    c = stdscr.getch()
                    if c in (27, 113):  # ESC, q
                        quit_game = True
                    elif c == ord('b'):
                        rewind = True
                if quit_game:
                    break
                if rewind:
                    if not history:
                        stdscr.addstr(map.height()+1, 0, 'no more history')
                        stdscr.refresh()
                    else:
                        map = history.pop()
                    continue
                history.append(copy.deepcopy(map))
            with log_context('step'):
                map.step()
    finally:
        curses.nocbreak()
        stdscr.keypad(0)
        curses.echo()
        curses.endwin()
        print "Tick {0} Score {1}".format(map.current_tick,
                                          map.lambdaman.score)


if __name__ == '__main__':
    main()
