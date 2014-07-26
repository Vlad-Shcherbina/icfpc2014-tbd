import nose
from nose.tools import eq_, assert_raises
from itertools import izip_longest
from collections import namedtuple

from asm_parser import pre_parse, ParsingException, ParsedInstruction, MODE_GCC, MODE_GHC
from asm_parser import parse_gcc

def assert_lists_equal(lst1, lst2):
    sentinel = namedtuple('ItemNotPresent', '')
    for i, (it1, it2) in enumerate(izip_longest(lst1, lst2, fillvalue=sentinel)):
        eq_(it1, it2, '{}-th item differ: {!r} != {!r}'.format(i, it1, it2)) 

def assert_dicts_equal(d1, d2):
    sentinel = namedtuple('ItemNotPresent', '')
    for it1, it2 in izip_longest(sorted(d1.iteritems()), sorted(d2.iteritems()), fillvalue=sentinel):
        eq_(it1, it2) 


def test_strictness():
    assert_raises(ParsingException, pre_parse, 'label:', MODE_GCC, strict=True) 
    assert_raises(ParsingException, pre_parse, 'label:\nlabel:', MODE_GCC) 
    assert_raises(ParsingException, pre_parse, '1label:', MODE_GCC)
    assert_raises(ParsingException, pre_parse, 'LD   0, 0', MODE_GCC)
    assert_raises(ParsingException, pre_parse, 'and   a 1', MODE_GHC)
    
    parse_gcc('label1: LDF   label1\nlabel2:')
    assert_raises(ParsingException, parse_gcc, 'label1: LDF   0 1\nlabel2:')
    assert_raises(ParsingException, parse_gcc, 'label1: LDF1   0\nlabel2:')
    assert_raises(ParsingException, parse_gcc, 'label1: LDF   label2\nlabel2:')
    
def test_regressions():
    parse_gcc('    ldc -1')
    
def test_gcc():
    code = '''
  DUM  2        ; 2 top-level declarations
  LDF  go       ; declare function go
  LDF  to       ; declare function to
  LDF  main     ; main function
  RAP  2        ; load declarations into environment and run main
  RTN           ; final return
main:
  LDC  -1
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
  RTN'''
    parsed = pre_parse(code, MODE_GCC)
    expected = ([
            ParsedInstruction(op='DUM', args=['2'], line=2, source='<unnamed code>', original_text='  DUM  2        ; 2 top-level declarations'),
            ParsedInstruction(op='LDF', args=['go'], line=3, source='<unnamed code>', original_text='  LDF  go       ; declare function go'),
            ParsedInstruction(op='LDF', args=['to'], line=4, source='<unnamed code>', original_text='  LDF  to       ; declare function to'),
            ParsedInstruction(op='LDF', args=['main'], line=5, source='<unnamed code>', original_text='  LDF  main     ; main function'),
            ParsedInstruction(op='RAP', args=['2'], line=6, source='<unnamed code>', original_text='  RAP  2        ; load declarations into environment and run main'),
            ParsedInstruction(op='RTN', args=[], line=7, source='<unnamed code>', original_text='  RTN           ; final return'),
            ParsedInstruction(op='LDC', args=['-1'], line=9, source='<unnamed code>', original_text='  LDC  -1'),
            ParsedInstruction(op='LD', args=['0', '0'], line=10, source='<unnamed code>', original_text='  LD   0 0      ; var go'),
            ParsedInstruction(op='AP', args=['1'], line=11, source='<unnamed code>', original_text='  AP   1        ; call go(1)'),
            ParsedInstruction(op='RTN', args=[], line=12, source='<unnamed code>', original_text='  RTN'),
            ParsedInstruction(op='LD', args=['0', '0'], line=14, source='<unnamed code>', original_text='  LD   0 0      ; var n'),
            ParsedInstruction(op='LDC', args=['1'], line=15, source='<unnamed code>', original_text='  LDC  1'),
            ParsedInstruction(op='SUB', args=[], line=16, source='<unnamed code>', original_text='  SUB'),
            ParsedInstruction(op='LD', args=['1', '0'], line=17, source='<unnamed code>', original_text='  LD   1 0      ; var go'),
            ParsedInstruction(op='AP', args=['1'], line=18, source='<unnamed code>', original_text='  AP   1        ; call go(n-1)'),
            ParsedInstruction(op='RTN', args=[], line=19, source='<unnamed code>', original_text='  RTN'),
            ParsedInstruction(op='LD', args=['0', '0'], line=21, source='<unnamed code>', original_text='  LD   0 0      ; var n'),
            ParsedInstruction(op='LDC', args=['1'], line=22, source='<unnamed code>', original_text='  LDC  1'),
            ParsedInstruction(op='ADD', args=[], line=23, source='<unnamed code>', original_text='  ADD'),
            ParsedInstruction(op='LD', args=['1', '1'], line=24, source='<unnamed code>', original_text='  LD   1 1      ; var to'),
            ParsedInstruction(op='AP', args=['1'], line=25, source='<unnamed code>', original_text='  AP   1        ; call to(n+1)'),
            ParsedInstruction(op='RTN', args=[], line=26, source='<unnamed code>', original_text='  RTN')],
            {'go': 16, 'main': 6, 'to': 10})
    assert_lists_equal(parsed[0], expected[0])
    assert_dicts_equal(parsed[1], expected[1])
    parsed = parse_gcc(code)
    expected = ([
            ParsedInstruction(op='DUM', args=[2], line=2, source='<unnamed code>', original_text='  DUM  2        ; 2 top-level declarations'),
            ParsedInstruction(op='LDF', args=[16], line=3, source='<unnamed code>', original_text='  LDF  go       ; declare function go'),
            ParsedInstruction(op='LDF', args=[10], line=4, source='<unnamed code>', original_text='  LDF  to       ; declare function to'),
            ParsedInstruction(op='LDF', args=[6], line=5, source='<unnamed code>', original_text='  LDF  main     ; main function'),
            ParsedInstruction(op='RAP', args=[2], line=6, source='<unnamed code>', original_text='  RAP  2        ; load declarations into environment and run main'),
            ParsedInstruction(op='RTN', args=[], line=7, source='<unnamed code>', original_text='  RTN           ; final return'),
            ParsedInstruction(op='LDC', args=[-1], line=9, source='<unnamed code>', original_text='  LDC  -1'),
            ParsedInstruction(op='LD', args=[0, 0], line=10, source='<unnamed code>', original_text='  LD   0 0      ; var go'),
            ParsedInstruction(op='AP', args=[1], line=11, source='<unnamed code>', original_text='  AP   1        ; call go(1)'),
            ParsedInstruction(op='RTN', args=[], line=12, source='<unnamed code>', original_text='  RTN'),
            ParsedInstruction(op='LD', args=[0, 0], line=14, source='<unnamed code>', original_text='  LD   0 0      ; var n'),
            ParsedInstruction(op='LDC', args=[1], line=15, source='<unnamed code>', original_text='  LDC  1'),
            ParsedInstruction(op='SUB', args=[], line=16, source='<unnamed code>', original_text='  SUB'),
            ParsedInstruction(op='LD', args=[1, 0], line=17, source='<unnamed code>', original_text='  LD   1 0      ; var go'),
            ParsedInstruction(op='AP', args=[1], line=18, source='<unnamed code>', original_text='  AP   1        ; call go(n-1)'),
            ParsedInstruction(op='RTN', args=[], line=19, source='<unnamed code>', original_text='  RTN'),
            ParsedInstruction(op='LD', args=[0, 0], line=21, source='<unnamed code>', original_text='  LD   0 0      ; var n'),
            ParsedInstruction(op='LDC', args=[1], line=22, source='<unnamed code>', original_text='  LDC  1'),
            ParsedInstruction(op='ADD', args=[], line=23, source='<unnamed code>', original_text='  ADD'),
            ParsedInstruction(op='LD', args=[1, 1], line=24, source='<unnamed code>', original_text='  LD   1 1      ; var to'),
            ParsedInstruction(op='AP', args=[1], line=25, source='<unnamed code>', original_text='  AP   1        ; call to(n+1)'),
            ParsedInstruction(op='RTN', args=[], line=26, source='<unnamed code>', original_text='  RTN')])
    assert_lists_equal(parsed, expected)




def test_ghc():
    code = '''
; Go up if our x-ordinate is even, or down if it is odd.
int 3          ; Get our ghost index in A.
int 5          ; Get our x-ordinate in A.
and a,1        ; Zero all but least significant bit of A.
               ; Now A is 0 if x-ordinate is even, or 1 if it is odd.
mov b,a        ; Save A in B because we need to use A to set direction.
mov a,2        ; Move down by default.
jeq 7,b,1      ; Don't change anything if x-ordinate is odd.
mov a,0        ; We only get here if x-ordinate was even, so move up.
int 0          ; This is line 7, the target of the above jump. Now actually set the direction.
hlt            ; Stop.
    '''
    
if __name__ == '__main__':
    nose.run_exit(argv=['--verbose'])