from unittest import TestCase
from game import *


class GameTest(TestCase):
    def test_map(self):
        lines = ["####", "#\=#", "####"]
        ghost_ais = [GhostAI("")]
        map = Map(lines, ghost_ais)
        self.assertEquals(WALL, map.at(0, 0))
        self.assertEquals(LAMBDAMAN, map.at(1, 1))
        self.assertEquals(GHOST, map.at(2, 1))
