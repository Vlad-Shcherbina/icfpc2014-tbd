from unittest import TestCase
from game import Map
from gcc_wrapper import GCCWrapper, GCCInterface


class DummyGCCInterface(GCCInterface):
    pass


class GCCWrapperTest(TestCase):
    def setUp(self):
        super(GCCWrapperTest, self).setUp()
        self.map = Map(["#####", "#\.=#", "#####"],
                       ["ghc:miner.ghc"], "interactive:")
        self.wrapper = GCCWrapper(DummyGCCInterface())

    def test_encode_map(self):
        encoded = self.wrapper.encode_map(self.map)
        self.assertEquals([[0, 0, 0, 0, 0], [0, 5, 2, 6, 0], [0, 0, 0, 0, 0]],
                          encoded)

    def test_encode_lman(self):
        encoded = self.wrapper.encode_lman(self.map)
        # vitality, coords, direction, lives, score
        self.assertEquals((0, (1, 1), 2, 3, 0), encoded)

    def test_encode_ghosts(self):
        encoded = self.wrapper.encode_ghosts(self.map)
        # vitality, coords, direction
        self.assertEquals([(0, (3, 1), 2)], encoded)