import ast
import os
import pprint
import argparse

from gcc_ast_converter import convert_python_to_gcc_module
from gcc_ast import GccTextBuilder
from asm_parser import parse_gcc
from yole_gcc import GccMachine
from map_loader import load_map
from gcc_wrapper import GCCWrapper


def compile_to_text(source_file, disable_tco=True):
    with open(os.path.join('../data/gcpy', source_file), 'r') as f:
        code = f.read()
    python_ast = ast.parse(code)
    gcc_program = convert_python_to_gcc_module(python_ast)
    builder = GccTextBuilder()
    gcc_program.emit(builder, disable_tco=disable_tco)
    return builder.text


def compile(source_file, disable_tco=True):
    return parse_gcc(compile_to_text(source_file, disable_tco))


def main():
    parser = argparse.ArgumentParser(description="Run a greatly castrated python script")
    parser.add_argument('-p', help='program to compile and run', dest='program')
    parser.add_argument('-m', help='map to use', dest='map', default='default_map.txt')
    parser.add_argument('-a', help='program arguments', dest='args', nargs='+', type=int, default=[])
    parser.add_argument('-o', help='code output file', dest='output_file', default=None)
    parser.add_argument('-c', help='compile only', dest='compile_only', action='store_const', const=True, default=False)
    parser.add_argument('--no-tco', help='disable TCO', dest='disable_tco', action='store_const', const=True, default=False)
    #parser.add_argument('-r', help='program arguments', dest='run', type=bool, default=False)
    args = parser.parse_args()
    if not args.program: return
    text = compile_to_text(args.program, disable_tco=args.disable_tco)
    if args.output_file is not None:
        with open(args.output_file, 'w') as f:
            f.write(text + '\n')
    else:
        print text
    if args.compile_only: return
    machine = GccMachine(parse_gcc(text))
    wrapper = GCCWrapper(machine)
    map = load_map(args.map)
    world_state = wrapper.marshal_world_state(map)
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(machine.call(0, world_state, *(args.args)))

if __name__ == "__main__":
    main()
