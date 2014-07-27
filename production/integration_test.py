import os
from unittest import TestCase
import ast

from game import POWER_PILL, PILL, GHOST
from gcc_ast_converter import convert_python_to_gcc_module
from gcc_ast import GccTextBuilder
from asm_parser import parse_gcc
from yole_gcc import GccMachine
from map_loader import load_map
from gcc_wrapper import GCCWrapper


class IntegrationTest(TestCase):
    def prepare(self, map_file, script):
        text = open(os.path.join("../data/gcpy", script)).read()
        python_ast = ast.parse(text)
        gcc_program = convert_python_to_gcc_module(python_ast)
        builder = GccTextBuilder()
        gcc_program.emit(builder)
        self.machine = GccMachine(parse_gcc(builder.text), builder)
        self.wrapper = GCCWrapper(self.machine)
        self.map = load_map(map_file)
        self.world_state = self.wrapper.marshall_world_state(self.map)

    def test_get_cell_at(self):
        self.prepare("default_map.txt", "get_cell_at.py")
        result = self.machine.call(0, self.world_state[0], 1, 1)
        self.assertEquals(PILL, result)
        result = self.machine.call(0, self.world_state[0], 1, 3)
        self.assertEquals(POWER_PILL, result)

    def test_get_adjacent_cell(self):
        self.prepare("default_map.txt", "get_adjacent_cell.py")
        result = self.machine.call(0, self.world_state, 1, 0)
        self.assertEquals(PILL, result)
        result = self.machine.call(0, self.world_state, 0, -6)
        self.assertEquals(GHOST, result)

    def test_list_length(self):
        self.prepare("default_map.txt", "list_length.py")
        result = self.machine.call(0, self.world_state[0])
        self.assertEquals(22, result)

    def test_best_pill_direction(self):
        self.prepare("default_map.txt", "best_pill_direction.py")
        result = self.machine.call(0, self.world_state)
        self.assertEquals(1, result)
        self.map.lambdaman.x = 20
        self.map.lambdaman.y = 16
        self.world_state = self.wrapper.marshall_world_state(self.map)
        result = self.machine.call(0, self.world_state)
        self.assertEquals(3, result)

    def test_has_ghost_at(self):
        self.prepare("default_map.txt", "has_ghost_at.py")
        result = self.machine.call(0, self.world_state, 11, 8)
        self.assertEquals(1, result)
        result = self.machine.call(0, self.world_state, 12, 10)
        self.assertEquals(1, result)
        result = self.machine.call(0, self.world_state, 2, 2)
        self.assertEquals(0, result)
