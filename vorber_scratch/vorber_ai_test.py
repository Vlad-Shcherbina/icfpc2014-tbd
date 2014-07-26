import sys
sys.path.append('../production')
sys.path.append('../yole_scratch')
import ast
from unittest import TestCase
from gcc_ast_converter import convert_python_to_gcc_module
from gcc_ast import GccTextBuilder
from asm_parser import parse_gcc
from yole_gcc import GccMachine
from map_loader import load_map
from gcc_wrapper import GCCWrapper


class VorberAiTest(TestCase):
    def prepare(self, map_file, script):
        text = open(script).read()
        python_ast = ast.parse(text)
        gcc_program = convert_python_to_gcc_module(python_ast)
        builder = GccTextBuilder()
        gcc_program.emit(builder)
        self.machine = GccMachine(parse_gcc(builder.text))
        self.wrapper = GCCWrapper(self.machine)
        self.map = load_map(map_file)
        self.world_state = self.wrapper.marshall_world_state(self.map)

    def test_init(self):
        self.prepare("default_map.txt", "vorber_ai.py")
        result = self.machine.call(0, self.world_state[0], 5)
        self.assertEquals((11,16), result)


