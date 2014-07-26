import logging
log = logging.getLogger(__name__)

import re
from collections import namedtuple
from pprint import pprint
import peg_parser
from command_enums import GCC_CMD_ARGCOUNT , GCC_CMD_ADDR_ARGS

ParsedInstruction = namedtuple('ParsedInstruction', 'op, args, line, source, original_text')


MODE_GCC = 'gcc'
MODE_GHC = 'ghc'


class ParsingException(Exception):
    @staticmethod
    def from_inst(inst, msg):
        error = 'Parsing error at line {} in {!r}: {}\nline: {!r}'.format(inst.line, inst.source, msg, inst.original_text)
        raise ParsingException(error)


def pre_parse(text, mode, source='<unnamed code>', strict=False):
    '''Parse the generic asm syntax (more or less common for GHC and GCC), return a ([ParsedInstruction], {label:instruction})
    >>> 2 + 2
    4
    '''
    def raise_parsing_exception(msg):
        error = 'Parsing error at line {} in {!r}: {}\nline: {!r}'.format(line_idx, source, msg, orig_line)
        raise ParsingException(error)
    
    grammar_src = '''
        labelled_instruction => label : instruction | label : | instruction 
        instruction => op \s+ arglist | op
        arglist => arg argsep arglist | arg
        op => [a-zA-Z]+
        arg => [\-a-zA-Z0-9\[\]]+
        label => [_a-zA-Z][_a-zA-Z0-9]*
        argsep => {}
    '''.format('\s+' if mode == MODE_GCC else ',')
    grammar = peg_parser.make_grammar(grammar_src)
    
    instructions = []
    labels = {}
    
    for line_idx, orig_line in enumerate(text.split('\n')):
        line_idx += 1 # 1-based, in case we need it.
        # remove comment
        line = re.sub(r';.*$', '', orig_line).strip()
        if not line: continue
        parsed, remainder = peg_parser.parse('labelled_instruction', grammar, line)
        if parsed is None:
            # we couldn't parse any part of the string at all.
            raise_parsing_exception('Parse failed immediately.')
        parsed = peg_parser.simplify_parse(parsed, ('label', 'op', 'arg'))
        parsed = peg_parser.filter_terminals(parsed)
        if remainder:
            raise_parsing_exception('Parse failed at {!r} after parsing {!r}'.format(remainder, parsed))
        op = None
        args = []
        for k, v in parsed:
            if k == 'label':
                if strict:
                    raise_parsing_exception('Labels are not allowed in the strict mode'.format(v))
                if v in labels:
                    raise_parsing_exception('Duplicate label: {}'.format(v))
                labels[v] = len(instructions)
            elif k == 'op':
                op = v.upper()
            elif k == 'arg':
                args.append(v)
            else:
                assert False
        if op:
            instructions.append(ParsedInstruction(op, args, line_idx, source, orig_line))
            
    return instructions, labels




def parse_gcc(text, source='<unnamed code>', strict=False):
    parsed, labels = pre_parse(text, MODE_GCC, source, strict)
    res = []
    for inst in parsed:
        # validate instruction
        argc = GCC_CMD_ARGCOUNT.get(inst.op)
        if argc is None:
            ParsingException.from_inst(inst, 'Unknown command: {}'.format(inst.op))
        if len(inst.args) != argc:
            ParsingException.from_inst(inst, 'Invalid number of arguments for {}: {} (expected {})'.format(
                    inst.op, len(inst.args), argc))
        # conver args to ints
        args = []
        for i, arg in enumerate(inst.args):
            if re.match(r'-?\d+$', arg):
                arg = int(arg)
            elif strict:
                # only numbers allowed
                ParsingException.from_inst(inst, 'Argument {} is invalid: {}'.format(i + 1, arg))
            elif re.match(r'-?0[x0b]\d+$', arg):
                arg = int(arg, 0) # support hex and octal and shit
                # note that we don't accidentally parse 0123 as octal because it's already handled 
            elif arg in labels:
                arg = labels[arg]
            else:
                ParsingException.from_inst(inst, 'Argument {} is invalid: {}'.format(i + 1, arg))
            # check that address is in range, just in case
            if inst.op in GCC_CMD_ADDR_ARGS:
                if arg >= len(parsed):
                    ParsingException.from_inst(inst, 'Argument {} is invalid, address too large: {} > {}'.format(i + 1, arg, len(parsed)))
            args.append(arg)
        res.append(inst._replace(args=args) if len(args) else inst)
    return res


if __name__ == '__main__':
    import nose, sys
    if not nose.run(argv=['--verbose', '--with-doctest']):
        sys.exit()
        
    pprint(parse_gcc('''
  DUM  2        ; 2 top-level declarations
  LDF  go       ; declare function go
  LDF  to       ; declare function to
  LDF  main     ; main function
  RAP  2        ; load declarations into environment and run main
  RTN           ; final return
main:
  LDC  1
  LD   0 0      ; var go
  AP   1        ; call go(1)
  RTN
to:
  LD   0 0      ; var n
  LDC  1
  SUB
  LD   1 0      ; var go
  AP   1        ; call go(n-1)
  RTN
go:
  LD   0 0      ; var n
  LDC  1
  ADD
  LD   1 1      ; var to
  AP   1        ; call to(n+1)
  RTN'''))
    