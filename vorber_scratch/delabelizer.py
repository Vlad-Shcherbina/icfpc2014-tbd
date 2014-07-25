#
# Comments out all labels in gcc code
# Replaces label references with command numbers
#
# Reads code from files in arguments or stdin
# Output written to stdout
#

import re
import fileinput

def delabelize(code_lines):
    label_re = re.compile('^\w*:')
    #remove empty and fully ws lines
    lines = code_lines
    
    command_index = 0
    line_index = 0
    expanded = []
    labels = []
    for line in lines:
        if label_re.match(line):
            #it is label!
            labels.append({'name':line[:-1], 'ci':command_index})
            expanded.append({'type':'label', 'line':';'+line, 'ci':command_index, 'li':line_index})
        elif line.lstrip().startswith(';') or len(line.strip())==0:
            #it is comment or ws, add as is
            expanded.append({'type':'comment', 'line':line, 'ci':command_index, 'li':line_index})
        else:
            #looks like command
            expanded.append({'type':'command', 'line':line, 'ci':command_index,'li':line_index})
            command_index +=1
        line_index += 1

    result = []
    for e in expanded:
        if e['type'] == 'command':
            cmd = e['line']
            for l in labels:
                if cmd.find(l['name']) != -1:
                    cmd = cmd.replace(l['name'], str(l['ci']), 1) #replace first only
                    break #we don't handle cases when one command references >1 labels
            result.append(cmd)
        else:
            result.append(e['line'])
    return result

import sys

def main():
    new = delabelize(map(str.rstrip, fileinput.input()))
    
    sys.stdout.write('\n'.join(new))
    pass

if __name__ == '__main__':
    main()