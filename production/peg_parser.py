from functools import update_wrapper
from string import split
import re
from collections import defaultdict

# a simple PEG parser taken from Peter Norvig's "Design of Computer Programs" course at udacity and slightly modified

def make_grammar(description, whitespace=r'\s*'):
    """Convert a description to a grammar.  Each line is a rule for a
    non-terminal symbol; it looks like this:
        Symbol =>  A1 A2 ... | B1 B2 ... | C1 C2 ...
    where the right-hand side is one or more alternatives, separated by
    the '|' sign.  Each alternative is a sequence of atoms, separated by
    spaces.  An atom is either a symbol on some left-hand side, or it is
    a regular expression that will be passed to re.match to match a token.

    Notation for *, +, or ? not allowed in a rule alternative (but ok
    within a token). Use '\' to continue long lines.  You must include spaces
    or tabs around '=>' and '|'. That's within the grammar description itself.
    The grammar that gets defined allows whitespace between tokens by default;
    specify '' as the second argument to grammar() to disallow this (or supply
    any regular expression to describe allowable whitespace between tokens)."""
    G = {' ': whitespace}
    description = description.replace('\t', ' ') # no tabs!
    for line in split(description, '\n'):
        line = line.strip()
        if not line: continue
        lhs, rhs = split(line, ' => ', 1)
        alternatives = split(rhs, ' | ')
        assert lhs not in G
        G[lhs] = tuple(map(split, alternatives))
    return G

def decorator(d):
    def _d(fn):
        return update_wrapper(d(fn), fn)
    update_wrapper(_d, d)
    return _d

@decorator
def memo(f):
    cache = {}
    def _f(*args):
        try:
            return cache[args]
        except KeyError:
            cache[args] = result = f(*args)
            return result
        except TypeError:
            # some element of args can't be a dict key
            return f(args)
    return _f

Fail = (None, None)

def parse(start_symbol, grammar, text):
    """Example call: parse('Exp', G, '3*x + b').
    Returns a (tree, remainder) pair. If remainder is '', it parsed the whole
    string. Failure iff remainder is None. This is a deterministic PEG parser,
    so rule order (left-to-right) matters. Do 'E => T op E | T', putting the
    longest parse first; don't do 'E => T | T op E'
    Also, no left recursion allowed: don't do 'E => E op T'"""

    tokenizer = grammar[' '] + '(%s)'

    def parse_sequence(sequence, text):
        result = []
        for atom in sequence:
            tree, text = parse_atom(atom, text)
            if text is None: return Fail
            result.append(tree)
        return result, text

    @memo
    def parse_atom(atom, text):
        if atom in grammar:  # Non-Terminal: tuple of alternatives
            for alternative in grammar[atom]:
                tree, rem = parse_sequence(alternative, text)
                if rem is not None: return [atom]+tree, rem  
            return Fail
        else:  # Terminal: match characters against start of text
            m = re.match(tokenizer % atom, text)
            return Fail if (not m) else (m.group(1), text[m.end():])

    # Body of parse:
    return parse_atom(start_symbol, text)


def simplify_parse(parse, symbols):
    '''Walk the parse tree in order and remove nodes not in "symbols" by adding their children to the parent node.
    
    Returns a list of nodes, because what if we removed the top-level node?
    
    This is a monad, btw. Like, for reals.
    ''' 
    def rec(parse):
        if isinstance(parse, basestring):
            yield parse
        elif parse[0] in symbols:
            result = [parse[0]]
            for it in parse[1:]:
                result.extend(rec(it))
            yield result
        else:
            for it in parse[1:]:
                for it in rec(it):
                    yield it
    return list(rec(parse))
            

def filter_terminals(lst):
    return [it for it in lst if not isinstance(it, basestring)]    
    

def main():
    g = make_grammar('''
        labelled_instruction => label : instruction | label : | instruction 
        instruction => op arglist | op
        arglist => arg argsep arglist | arg
        op => [a-zA-Z]+
        arg => [a-zA-Z0-9\[\]]+
        label => [_a-zA-Z][_a-zA-Z0-9]*
        argsep => \s+
        ''')
    
    print parse('labelled_instruction', g, 'asdf: MUL [A] 1 3')  
    print parse('labelled_instruction', g, 'asdf:')
    print parse('labelled_instruction', g, 'INC')  
    p, _ = parse('labelled_instruction', g, 'asdf: MUL [A] 1 3')
    print filter_terminals(simplify_parse(p, ('label', 'op', 'arg')))  

if __name__ == '__main__':
    main()