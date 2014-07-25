import sys
from game import GhostAI, Map
import curses

lines = [line.strip() for line in open("../data/maps/default_map.txt").readlines()]
ghost_ais = [GhostAI("")]
map = Map(lines, ghost_ais)

stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(1)

try:
    for y in range(map.height()):
        stdscr.addstr(y, 0, map.line_as_text(y))
    stdscr.getch()
finally:
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()
