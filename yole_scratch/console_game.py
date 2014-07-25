import curses
import logging
import sys

import sys
sys.path.append('../production')
from game import GhostAI, Map, LambdaMan, InteractiveLambdaManAI

logging.basicConfig(level=logging.DEBUG, filename='debug.log')

DIRECTION_KEYS = [curses.KEY_UP, curses.KEY_RIGHT, curses.KEY_DOWN, curses.KEY_LEFT]

lman_ai = InteractiveLambdaManAI()
map_file = "../data/maps/default_map.txt"
if len(sys.argv) > 1:
    map_file = sys.argv[len(sys.argv) - 1]

lines = [line.strip('\n') for line in open(map_file).readlines()]

ghost_ais = [
    'ghc:fickle.ghc',
    'ghc:miner.ghc',
    'ghc:flipper.ghc',
]

#ghost_ais = ['py:GhostAI_Random']

map = Map(lines, ghost_ais, lman_ai)

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
        stdscr.addstr(map.height(), 0,
                      "Tick {0} Score {1}".format(map.move_queue[0].next_move,
                                                 map.lambdamen[0].score))
        stdscr.refresh()
        next_actor = map.move_queue[0]
        if isinstance(next_actor, LambdaMan):
            quit_game = False
            while True:
                c = stdscr.getch()
                if c == 27:
                    quit_game = True
                    break
                if c in DIRECTION_KEYS:
                    lman_ai.direction = DIRECTION_KEYS.index(c)
                    break
                stdscr.addstr(map.height()+1, 0, "Unknown key " + str(c) + "  ")
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
