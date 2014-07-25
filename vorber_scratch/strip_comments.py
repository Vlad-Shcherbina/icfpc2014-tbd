#
# Strips all comments from file
#
# Reads code from files in arguments or stdin
# Output written to stdout
#

import re
import fileinput

def strip_comments(code_lines):
    lines = code_lines
    result = []
    for l in lines:
        i = l.find(';')
        if i != -1:
            result.append(l[:i])
    return result

import sys

def main():
    new = strip_comments(map(str.rstrip, fileinput.input()))
    sys.stdout.write('\n'.join(new))
    pass

if __name__ == '__main__':
    main()