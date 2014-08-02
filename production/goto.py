# from http://code.activestate.com/recipes/576944/

import dis
import new


class MissingLabelError(Exception):
    """'goto' without matching 'label'."""
    pass


class DuplicateLabelError(Exception):
    pass


def goto(fn):
    """
    A function decorator to add the goto command for a function.

    Specify labels like so:

    label .foo

    Goto labels like so:

    goto .foo
    """
    assert fn.func_code.co_freevars == (), "don't use for nested functions"
    labels = {}
    gotos = []
    global_name = None
    end = len(fn.func_code.co_code)
    i = 0

    # scan through the byte codes to find the labels and gotos
    while i < end:
        op = ord(fn.func_code.co_code[i])
        i += 1
        name = dis.opname[op]

        if op > dis.HAVE_ARGUMENT:
            b1 = ord(fn.func_code.co_code[i])
            b2 = ord(fn.func_code.co_code[i + 1])
            num = b2 * 256 + b1

            if name == 'LOAD_GLOBAL':
                global_name = fn.func_code.co_names[num]
                index = i - 1
                i += 2
                continue

            if name == 'LOAD_ATTR':
                if global_name == 'label':
                    label = fn.func_code.co_names[num]
                    if label in labels:
                        raise DuplicateLabelError("Duplicate label: %s" % label)
                    labels[label] = index
                elif global_name == 'goto':
                    label = fn.func_code.co_names[num]
                    gotos.append((label, index))

            i += 2
        global_name = None

    # no-op the labels
    ilist = list(fn.func_code.co_code)
    for label, index in labels.items():
        ilist[index:index+7] = [chr(dis.opmap['NOP'])]*7

    # change gotos to jumps
    for label, index in gotos:
        if label not in labels:
            raise MissingLabelError("Missing label: %s"%label)

        target = labels[label] + 7   # skip NOPs
        ilist[index] = chr(dis.opmap['JUMP_ABSOLUTE'])
        ilist[index + 1] = chr(target & 255)
        ilist[index + 2] = chr(target >> 8)

    # create new function from existing function
    c = fn.func_code
    newcode = new.code(c.co_argcount,
                       c.co_nlocals,
                       c.co_stacksize,
                       c.co_flags,
                       ''.join(ilist),
                       c.co_consts,
                       c.co_names,
                       c.co_varnames,
                       c.co_filename,
                       c.co_name,
                       c.co_firstlineno,
                       c.co_lnotab)
    newfn = new.function(newcode,fn.func_globals)
    return newfn
