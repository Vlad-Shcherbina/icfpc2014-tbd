class GCC_CMD(object):
    __slots__ = []
    LDC  = 'LDC'
    LD   = 'LD'
    ADD  = 'ADD'
    SUB  = 'SUB'
    MUL  = 'MUL'
    DIV  = 'DIV'
    CEQ  = 'CEQ'
    CGT  = 'CGT'
    CGTE = 'CGTE'
    ATOM = 'ATOM'
    CONS = 'CONS'
    CAR  = 'CAR'
    CDR  = 'CDR'
    SEL  = 'SEL'
    JOIN = 'JOIN'
    LDF  = 'LDF'
    AP   = 'AP'
    RTN  = 'RTN'
    DUM  = 'DUM'
    RAP  = 'RAP'
    STOP = 'STOP'
    TSEL = 'TSEL'
    TAP  = 'TAP'
    TRAP = 'TRAP'
    ST   = 'ST'
    DBUG = 'DBUG'
    BRK  = 'BRK'

GCC_CMD_ARGCOUNT = {
        GCC_CMD.LDC:  1,
        GCC_CMD.LD:   2,
        GCC_CMD.ADD:  0,
        GCC_CMD.SUB:  0,
        GCC_CMD.MUL:  0,
        GCC_CMD.DIV:  0,
        GCC_CMD.CEQ:  0,
        GCC_CMD.CGT:  0,
        GCC_CMD.CGTE: 0,
        GCC_CMD.ATOM: 0,
        GCC_CMD.CONS: 0,
        GCC_CMD.CAR:  0,
        GCC_CMD.CDR:  0,
        GCC_CMD.SEL:  2,
        GCC_CMD.JOIN: 0,
        GCC_CMD.LDF:  1,
        GCC_CMD.AP:   1,
        GCC_CMD.RTN:  0,
        GCC_CMD.DUM:  1,
        GCC_CMD.RAP:  1,
        GCC_CMD.STOP: 0,
        GCC_CMD.TSEL: 2,
        GCC_CMD.TAP:  1,
        GCC_CMD.TRAP: 1,
        GCC_CMD.ST:   2,
        GCC_CMD.DBUG: 0,
        GCC_CMD.BRK:  0,
        }

GCC_CMD_ADDR_ARGS = frozenset((GCC_CMD.SEL, GCC_CMD.LDF, GCC_CMD.TSEL))

