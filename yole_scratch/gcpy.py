import ast
import game
from gcc_ast_converter import convert_python_to_gcc_module
from gcc_ast import GccTextBuilder
from asm_parser import parse_gcc
from yole_gcc import GccMachine
from map_loader import load_map
from gcc_wrapper import GCCWrapper

import pprint

import argparse
parser = argparse.ArgumentParser(description="Run a greatly castrated python script")
parser.add_argument('-p', help='program to run', dest='program')
parser.add_argument('-m', help='map to use', dest='map', default='default_map.txt')
parser.add_argument('-a', help='program arguments', dest='args', nargs='+', type=int, default=[])
#parser.add_argument('-r', help='program arguments', dest='run', type=bool, default=False)

if __name__ == "__main__":
  args = parser.parse_args()
  if(args.program):
    pp = pprint.PrettyPrinter(indent=2)
    code = open(args.program).read()
    python_ast = ast.parse(code)
    gcc_program = convert_python_to_gcc_module(python_ast)
    builder = GccTextBuilder()
    gcc_program.emit(builder)
    print(builder.text)
    machine = GccMachine(parse_gcc(builder.text))
    wrapper = GCCWrapper(machine)
    map = load_map(args.map)
    world_state = wrapper.marshall_world_state(map)
    pp.pprint(machine.call(0, world_state, *(args.args)))
