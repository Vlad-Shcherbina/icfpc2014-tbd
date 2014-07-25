from unittest import TestCase

from game import *


class GameTest(TestCase):
    def test_map(self):
        lines = ["####", r"#\=#", "####"]
        map = Map(lines, [""], InteractiveLambdaManAI())
        self.assertEquals(WALL, map.at(0, 0))
        self.assertEquals(LAMBDAMAN, map.at(1, 1))
        self.assertEquals(GHOST, map.at(2, 1))

    def test_step(self):
        lines = ["######", r"#\.%#", "#####"]
        ghost_ais = [""]
        lman_ai = InteractiveLambdaManAI()
        lman_ai.direction = RIGHT
        map = Map(lines, ghost_ais, lman_ai)
        map.step()
        lman = map.lambdamen[0]
        self.assertEquals(2, lman.x)
        self.assertEquals(10, lman.score)
        self.assertEquals(EMPTY, map.at(2, 1))
        self.assertEquals(map.move_queue[0], lman)
        self.assertEquals(264, lman.next_move)

    def test_expire_fruits(self):
        lines = ["#####", "#%..#", "#####"]
        map = Map(lines, [""], InteractiveLambdaManAI())
        self.assertEquals(EMPTY, map.at(1, 1))
        map.step()
        self.assertEquals(FRUIT, map.at(1, 1))
        map.step()
        self.assertEquals(EMPTY, map.at(1, 1))
        self.assertEquals(0, len(map.move_queue))
