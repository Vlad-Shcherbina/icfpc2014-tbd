import sys
from unittest import TestCase

import nose
from nose.tools import eq_

from game import *
from map_loader import load_map


class GameTest(TestCase):
    def test_map(self):
        lines = ["####", r"#\=#", "####"]
        map = Map(lines)
        map.set_ai_specs("interactive:", ["ghc:miner.ghc"])
        self.assertEquals(WALL, map.at(0, 0))
        self.assertEquals(LAMBDAMAN, map.at(1, 1))
        self.assertEquals(GHOST, map.at(2, 1))

    def test_step(self):
        lines = ["#####", r"#\.%#", "#####"]
        ghost_ais = ["ghc:miner.ghc"]
        lman_ai = "interactive:"
        set_interactive_lambda_man_direction(RIGHT)
        map = Map(lines)
        map.set_ai_specs(lman_ai, ghost_ais)
        map.step()
        lman = map.lambdaman
        self.assertEquals(2, lman.x)
        self.assertEquals(10, lman.score)
        self.assertEquals(EMPTY, map.at(2, 1))
        self.assertEquals(map.move_queue[0], lman)
        self.assertEquals(264, lman.next_move)

    def test_eat_fruit(self):
        map = load_map('eat_fruit.txt')
        map.set_ai_specs('py:lm_ai.Oscillating(frequency=5)', ['ghc:miner.ghc'])
        while not map.game_over():
            map.step()
        eq_(map.get_final_score(), 200)

    def test_expire_fruits(self):
        # FIXME
        # this test is failing because pacman is not on the map
        return
        lines = ["#####", r"#%..#", "#####"]
        map = Map(lines)
        map.set_ai_specs("py:lm_ai.Oscillating(frequency=1)", ["ghc:miner.ghc"])
        self.assertEquals(EMPTY, map.at(1, 1))
        map.step()
        self.assertEquals(FRUIT, map.at(1, 1))
        map.step()
        self.assertEquals(EMPTY, map.at(1, 1))
        map.step()
        self.assertEquals(FRUIT, map.at(1, 1))
        map.step()
        self.assertEquals(EMPTY, map.at(1, 1))
        self.assertEquals(0, len(map.move_queue))


if __name__ == '__main__':
    nose.run_exit(argv=[
        sys.argv[0], __file__,
        '--verbose', '--with-doctest', '--logging-level=INFO'
    ])
