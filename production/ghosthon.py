import sys

'''
this monstrosity converts ghosthon programs into GHC assembler.
ghosthon programs consist of

- GHC assembler commands, like "mov a, b"
- nicer mnemonics for interrupts:
    report, lambdaman, xxx, myindex, ghoststart, ghostpos, ghoststats, mapq, debug
- aliases (e.g. alias ptr [0], alias cnstnt 42, alias importantregister a)
- labels (by appending "| labelname" at the end of any line, but before comments),
    later usable like "jmp /labelname/"
- jmp <address>
- if <a> <op> <b> or ifnot <a> <op> <b> blocks, possibly with else blocks
- while <a> <op> <b> or whilenot <a> <op> <b> blocks

<a> and <b> denote parameters, which can be anything accepted by the GHC assembler.
op is one of <, =, >.

ifnot is a bit more effective than if when used without elses,
whilenot is a bit more effective than while.

blocks are indentation-delimited.

here's a sample program in ghosthon that counts from 1 to 10:

alias cnt [0]
mov cnt, 1     ; this is a sample comment
whilenot cnt = 11
    !debug
    inc cnt

ifnot cnt = 11
    ; wtf?!
    mov cnt, 6
    !debug
else
    ; output some nice zeroes
    mov cnt, 0
    !debug
'''

def count_indentation(line):
    n = 0
    while (n < len(line)) and line[n].isspace():
        n += 1
    return n

def error(desc):
    raise Exception('error: {}'.format(desc))

INTERRUPTS = ['report', 'lambdaman', 'xxx', 'myindex', 'ghoststart', 'ghostpos', 'ghoststats', 'mapq', 'debug']
MNEMONICS = ['mov', 'inc', 'dec', 'add', 'sub', 'mul', 'div', 'and', 'or', 'xor', 'jlt', 'jeq', 'jgt', 'int', 'hlt']
COMPARATORS = {'<': 'jlt', '=': 'jeq', '>': 'jgt'}
SINGLE_INDENT = 4

def make_indent_tree(code, indent_level=0):
    i = 0
    res = []
    while i < len(code):
        line = code[i].lower().strip()
        # remove comments & whitespace
        if ';' in line:
            line = line[:line.index(';')]

        # ignore empty lines
        if len(line) == 0:
            i += 1
            continue

        indent = count_indentation(code[i])
        if indent < indent_level:
            return res, i
        elif indent > indent_level:
            below_tree, below_lines = make_indent_tree(code[i:], indent)
            res.append(below_tree)
            i += below_lines
        else:
            res.append(line)
            i += 1

    return res, len(code)

def convert_tree(tree, aliases, labels, cmds_before=0):
    i = 0
    res = []
    while i < len(tree):
        line = tree[i]
        if isinstance(line, list): error('unexpected start of a block')

        if '|' in line:
            sep = line.index('|')
            label = line[sep+1:].strip()
            if (not label.isalpha()) or (len(label) == 1) or (label in MNEMONICS):
                error('invalid label "{}"'.format(label))
            if label in labels:
                error('trying to redefine label "{}"'.format(label))
            labels[label] = cmds_before + len(res)
            line = line[:sep].strip()

        if len(line) == 0:
            # this can happen with a line that only has a label
            i += 1
            continue

        if line.startswith('!'):
            # interrupt
            if line[1:] not in INTERRUPTS: error('unknown interrupt "{}"'.format(line))
            res.append(('int', [INTERRUPTS.index(line[1:])]))
            i += 1
        elif line.startswith('if'):
            # if / ifnot
            if not (line.startswith('if ') or line.startswith('ifnot ')):
                error('unknown construct "{}"'.format(line))

            ifnot = line.startswith('ifnot ')
            _, a, op, b = line.split()
            if op not in COMPARATORS: error('unknown comparison operator {}'.format(op))
            if a in aliases: a = aliases[a]
            if b in aliases: b = aliases[b]
            mnemonic = COMPARATORS[op]

            i += 1
            if i >= len(tree): error('unexpected end of block')
            if isinstance(tree[i], str): error('no new block following an if')
            body_tree = tree[i]
            i += 1

            else_tree = None
            if (i < len(tree)) and (tree[i] == 'else'):
                i += 1
                if i >= len(tree): error('unexpected end of block')
                if isinstance(tree[i], str): error('no new block following an else')
                else_tree = tree[i]
                i += 1

            if else_tree is None:
                if ifnot:
                    body_code = convert_tree(body_tree, aliases, labels, cmds_before=cmds_before + len(res) + 1)
                    res.append((mnemonic, [cmds_before + len(res) + len(body_code) + 1, a, b]))
                    res.extend(body_code)
                else:
                    res.append((mnemonic, [cmds_before + len(res) + 2, a, b]))
                    body_code = convert_tree(body_tree, aliases, labels, cmds_before=cmds_before + len(res) + 1)
                    res.append(('mov', ['pc', cmds_before + len(res) + 1 + len(body_code)]))
                    res.extend(body_code)
            else:
                if ifnot:
                    body_tree, else_tree = else_tree, body_tree

                else_code = convert_tree(else_tree, aliases, labels, cmds_before=cmds_before + len(res) + 1)
                res.append((mnemonic, [cmds_before + len(res) + 2 + len(else_code), a, b]))
                res.extend(else_code)
                body_code = convert_tree(body_tree, aliases, labels, cmds_before=cmds_before + len(res) + 1)
                res.append(('mov', ['pc', cmds_before + len(res) + 1 + len(body_code)]))
                res.extend(body_code)
        elif line.startswith('while'):
            # while / whilenot
            if not (line.startswith('while ') or line.startswith('whilenot ')):
                error('unknown construct "{}"'.format(line))
            whilenot = line.startswith('whilenot ')

            _, a, op, b = line.split()
            if op not in COMPARATORS: error('unknown comparison operator {}'.format(op))
            if a in aliases: a = aliases[a]
            if b in aliases: b = aliases[b]
            mnemonic = COMPARATORS[op]

            i += 1
            if i >= len(tree): error('unexpected end of block')
            if isinstance(tree[i], str): error('no new block following a while')
            body_tree = tree[i]
            i += 1

            if whilenot:
                body_code = convert_tree(body_tree, aliases, labels, cmds_before=cmds_before + len(res) + 1)
                back = cmds_before + len(res)
                res.append((mnemonic, [cmds_before + len(res) + len(body_code) + 2, a, b]))
                res.extend(body_code)
                res.append(('mov', ['pc', back]))
            else:
                body_code = convert_tree(body_tree, aliases, labels, cmds_before=cmds_before + len(res) + 2)
                back = cmds_before + len(res)
                res.append((mnemonic, [cmds_before + len(res) + 2, a, b]))
                res.append(('mov', ['pc', cmds_before + len(res) + len(body_code) + 2]))
                res.extend(body_code)
                res.append(('mov', ['pc', back]))
        elif line.startswith('alias '):
            # alias
            _, name, value = line.split()
            if (not name.isalpha()) or (len(name) == 1) or (name in MNEMONICS):
                error('invalid alias "{}"'.format(name))
            if name in aliases: error('trying to redefine alias "{}"'.format(name))
            aliases[name] = value
            i += 1
        elif line.startswith('jmp '):
            # jmp
            _, address = line.split()
            res.append(('mov', ['pc', address]))
            i += 1
        else:
            # some GHC mnemonic
            tokens = line.split()
            mnemonic = tokens[0]
            if mnemonic not in MNEMONICS:
                error('unknown GHC mnemonic "{}"'.format(mnemonic))
            args = ''.join(tokens[1:]).split(',')
            args = [aliases.get(x, x) for x in args]

            res.append((mnemonic, args))
            i += 1

    return res

def apply_labels(code, labels):
    def transform_arg(arg):
        if isinstance(arg, str) and arg.startswith('/') and arg.endswith('/'):
            name = arg[1:-1]
            if name not in labels: error('undefined label "{}"'.format(arg))
            return labels[name]
        return arg

    res = []
    for m, args in code:
        args = map(transform_arg, args)
        res.append((m, args))
    return res


def compile_into_ghc(code):
    tree, _ = make_indent_tree(code)
    labels = {}
    ghc_code = convert_tree(tree, {}, labels)
    ghc_code.append(('hlt', []))
    ghc_code = apply_labels(ghc_code, labels)
    return ghc_code


def full_compile(ghoston_code):
    code = ghoston_code.splitlines()
    ghc = compile_into_ghc(code)
    ghc = ['{} {}'.format(x, ','.join(map(str, y))) for (x, y) in ghc]

    # some pretty formatting
    offset = max(map(len, ghc)) + 1
    res = []
    for i, line in enumerate(ghc):
        res.append('{} {}; {}'.format(line, ' ' * (offset - len(line)), str(i).zfill(3)))

    return '\n'.join(res).upper()


def main():
    print full_compile(sys.stdin.read())


if __name__ == '__main__':
    main()
