import os
import unittest
import ast
import pprint

from gcc_utils import *
from gcc_ast_converter import convert_python_to_gcc_module
from gcc_ast import GccTextBuilder
from asm_parser import parse_gcc
from yole_gcc import GccMachine
from map_loader import load_map
from gcc_wrapper import GCCWrapper


def call(script, func_name, *args):
    text = open(os.path.join("../data/gcpy", script)).read()
    python_ast = ast.parse(text)
    gcc_program = convert_python_to_gcc_module(python_ast)
    builder = GccTextBuilder()
    gcc_program.emit(builder)
    print builder.text

    addr = builder.labels['$func_{}$'.format(func_name)]
    assert isinstance(addr, int)

    print '** calling {} at {}'.format(func_name, addr)
    print '** with args'
    for arg in args:
        pprint.pprint(arg)

    machine = GccMachine(parse_gcc(builder.text), builder)

    result = machine.call(addr, *args)

    print '** got result'
    pprint.pprint(result)

    return result


def list_length_test():
    assert call('list_length.py', 'list_length', list_to_gcc(range(5))) == 5
