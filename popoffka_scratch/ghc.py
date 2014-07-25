import logging

REGISTERS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'pc']
PC = REGISTERS.index('pc')

def condense_whitespace(str):
    res = []
    last_whitespace = True
    for ch in str:
        if ch.isspace():
            if not last_whitespace:
                res.append(' ')
            last_whitespace = True
        else:
            res.append(ch)
            last_whitespace = False
    return ''.join(res)

def parse_arg(x):
    if x in REGISTERS:
        return ('reg', REGISTERS.index(x))
    if x.isdigit() and (0 <= int(x) <= 255):
        return ('const', int(x))
    if (x[0] == '[') and (x[-1] == ']'):
        mid = x[1:-1]
        if mid in REGISTERS:
            assert mid != 'pc', 'PC cant be used as a pointer'
            return ('regp', REGISTERS.index(mid))
        if mid.isdigit() and (0 <= int(mid) <= 255):
            return ('ptr', int(mid))
    assert False, '{} cant be parsed as an argument'.format(x)


class GHC:
    def __init__(self, asm):
        # parse code
        self.code = []
        for line in asm.split('\n'):
            # remove comments, convert to lowercase, strip whitespace
            line = line.lower()
            line = condense_whitespace(line)
            if ';' in line:
                comment = line.index(';')
                line = line[:comment]
            line = line.strip()

            # ignore empty lines
            if len(line) == 0:
                continue

            if ' ' in line:
                sep = line.index(' ')
                mnemonic = line[:sep]
                args = [parse_arg(x.strip()) for x in line[sep + 1:].split(',')]
            else:
                mnemonic = line
                args = []

            self.code.append((mnemonic, args))

        # init memory
        self.data = bytearray(256)
        self.registers = bytearray(len(REGISTERS))
        self.halted = False
        self.instructions = {
            'mov': self.exec_mov,
            'inc': self.exec_inc,
            'dec': self.exec_dec,
            'add': self.exec_add,
            'sub': self.exec_sub,
            'mul': self.exec_mul,
            'div': self.exec_div,
            'and': self.exec_and,
            'or': self.exec_or,
            'xor': self.exec_xor,
            'jlt': self.exec_jlt,
            'jeq': self.exec_jeq,
            'jgt': self.exec_jgt,
            'int': self.exec_int,
            'hlt': self.exec_hlt,
        }

    def _assert(self, cond, message):
        'an assertion that will halt the GHC if the condition is false'
        if not cond:
            self.halted = True
            logging.debug('assertion failed: %s, %s', cond, message)

    def _get_value(self, arg):
        if arg[0] == 'reg':
            return self.registers[arg[1]]
        elif arg[0] == 'const':
            return arg[1]
        elif arg[0] == 'regp':
            return self.data[self.registers[arg[1]]]
        elif arg[0] == 'ptr':
            return self.data[arg[1]]

    def _set_value(self, arg, value):
        if arg[0] == 'reg':
            self.registers[arg[1]] = value
        elif arg[0] == 'const':
            assert False, 'implementation error: trying to assign to const'
        elif arg[0] == 'regp':
            self.data[self.registers[arg[1]]] = value
        elif arg[0] == 'ptr':
            self.data[arg[1]] = value

    def exec_mov(self, args):
        dst, src = args
        assert dst[0] != 'const', 'invalid dst for MOV'

        self._set_value(dst, self._get_value(src))

    def exec_inc(self, args):
        dst = args[0]
        assert dst[0] != 'const', 'invalid dst for INC'
        assert dst[0] != ('reg', 'pc'), 'invalid dst for INC'

        val = (self._get_value(dst) + 1) % 256
        self._set_value(dst, val)

    def exec_dec(self, args):
        dst = args[0]
        assert dst[0] != 'const', 'invalid dst for DEC'
        assert dst[0] != ('reg', 'pc'), 'invalid dst for DEC'

        val = (self._get_value(dst) + 255) % 256
        self._set_value(dst, val)

    def exec_add(self, args):
        dst, src = args
        assert dst[0] != 'const', 'invalid dst for ADD'
        assert dst[0] != ('reg', 'pc'), 'invalid dst for ADD'

        val = (self._get_value(dst) + self._get_value(src)) % 256
        self._set_value(dst, val)

    def exec_sub(self, args):
        dst, src = args
        assert dst[0] != 'const', 'invalid dst for SUB'
        assert dst[0] != ('reg', 'pc'), 'invalid dst for SUB'

        val = (self._get_value(dst) - self._get_value(src) + 256) % 256
        self._set_value(dst, val)

    def exec_mul(self, args):
        dst, src = args
        assert dst[0] != 'const', 'invalid dst for MUL'
        assert dst[0] != ('reg', 'pc'), 'invalid dst for MUL'

        val = (self._get_value(dst) * self._get_value(src)) % 256
        self._set_value(dst, val)

    def exec_div(self, args):
        dst, src = args
        assert dst[0] != 'const', 'invalid dst for DIV'
        assert dst[0] != ('reg', 'pc'), 'invalid dst for DIV'

        d = self._get_value(src)
        self._assert(d != 0, 'division by zero')
        if self.halted: return

        val = self._get_value(dst) / d
        self._set_value(dst, val)

    def exec_and(self, args):
        dst, src = args
        assert dst[0] != 'const', 'invalid dst for AND'
        assert dst[0] != ('reg', 'pc'), 'invalid dst for AND'

        val = self._get_value(dst) & self._get_value(src)
        self._set_value(dst, val)

    def exec_or(self, args):
        dst, src = args
        assert dst[0] != 'const', 'invalid dst for OR'
        assert dst[0] != ('reg', 'pc'), 'invalid dst for OR'

        val = self._get_value(dst) | self._get_value(src)
        self._set_value(dst, val)

    def exec_xor(self, args):
        dst, src = args
        assert dst[0] != 'const', 'invalid dst for XOR'
        assert dst[0] != ('reg', 'pc'), 'invalid dst for XOR'

        val = self._get_value(dst) ^ self._get_value(src)
        self._set_value(dst, val)

    def exec_jlt(self, args):
        targ, x, y = args
        if self._get_value(x) < self._get_value(y):
            self.pc = self._get_value(targ)

    def exec_jeq(self, args):
        targ, x, y = args
        if self._get_value(x) == self._get_value(y):
            self.pc = self._get_value(targ)

    def exec_jgt(self, args):
        targ, x, y = args
        if self._get_value(x) > self._get_value(y):
            self.pc = self._get_value(targ)

    def exec_int(self, args):
        which = self._get_value(args[0])
        assert 0 <= which <= 8, 'unknown interrupt {}'.format(which)

        if which != 8:
            logging.warning('STUB INTERRUPT IMPLEMENTATION (%s)', which)

        if which == 0:
            logging.debug('INT0: set dir to %s', self.registers[0])
        elif which == 1:
            self.registers[0] = 1
            self.registers[1] = 1
        elif which == 2:
            self.registers[0] = 1
            self.registers[1] = 1
        elif which == 3:
            self.registers[0] = 0
        elif which == 4:
            self.registers[0] = 1
            self.registers[1] = 1
        elif which == 5:
            self.registers[0] = 1
            self.registers[1] = 1
        elif which == 6:
            self.registers[0] = 1
            self.registers[1] = 1
        elif which == 7:
            self.registers[0] = 0
        elif which == 8:
            logging.debug('outputting registers: %s', map(int, self.registers))


    def exec_hlt(self, args):
        self.halted = True

    def execute(self, instruction):
        'executes a single instruction'
        mnemonic, args = instruction
        assert mnemonic in self.instructions, 'unknown mnemonic {}'.format(mnemonic)
        self.instructions[mnemonic](args)

    def run(self):
        'runs a single game cycle: up to 1024 instructions'
        cycles = 0
        self.registers[PC] = 0
        self.halted = False
        while not self.halted and (cycles < 1024):
            pc = self.registers[PC]
            self.execute(self.code[pc])
            if self.registers[PC] == pc:
                self.registers[PC] = (self.registers[PC] + 1) % 256
            cycles += 1

def main():
    logging.basicConfig(level=logging.DEBUG)
    code = '''
    ADD B, 5 ; hello
    ; this is example code
    MOV A, B
    MOV C, B
    MUL C, A
    INT 8
    HLT
    '''
    ghc = GHC(code)
    ghc.run()

if __name__ == '__main__':
    main()
