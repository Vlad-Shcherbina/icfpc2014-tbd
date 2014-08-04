import sys

sys.path.append('../vorber_scratch')
from cfg_builder import CfgBuilder
from delabelizer import delabelize


class AghostBuilder(CfgBuilder):
    """ Abstract-interpretation-based (sort of) ghost compiler. """

    def faked_globals(self):
        builder = self
        builder.next_temp = 100

        def make_temp():
            assert builder.next_temp < 200
            builder.next_temp += 1
            return Atom('[{}]'.format(builder.next_temp - 1))

        class Expression(object):
            def __add__(self, other):
                return BinaryOp('ADD', self, other)
            def __sub__(self, other):
                return BinaryOp('SUB', self, other)
            def __rsub__(self, other):
                return BinaryOp('SUB', other, self)
            def __mul__(self, other):
                return BinaryOp('MUL', self, other)
            def __div__(self, other):
                return BinaryOp('DIV', self, other)
            def compare(self, other, op):
                other = Expression.ensure(other)
                label = builder.get_simple_label(skip=1)
                label += '{{{}{}{}}}'.format(self, {'JEQ':'==', 'JLT':'<', 'JGT':'>'}[op],other)
                builder.branch({None: label + '?'})
                left = self.materialize()
                right = other.materialize()
                builder.add_statement('{} __jump_dst, {}, {}'.format(op, left, right))
                return builder.branch({True: label + '-true', False: label + '-false'})
            def __eq__(self, other):
                return self.compare(other, 'JEQ')
            def __lt__(self, other):
                return self.compare(other, 'JLT')
            def __gt__(self, other):
                return self.compare(other, 'JGT')
            def __ne__(self, other):
                return not self == other
            def __le__(self, other):
                return not self > other
            def __ge__(self, other):
                return not self < other
            @staticmethod
            def ensure(x):
                if isinstance(x, int):
                    return Atom(x)
                assert isinstance(x, Expression), x
                return x

        class BinaryOp(Expression):
            def __init__(self, op, left, right):
                left = Expression.ensure(left)
                right = Expression.ensure(right)
                self.op = op
                self.left = left
                self.right = right
                self.place = None
            def __str__(self):
                return '{}({},{})'.format(self.op, self.left, self.right)
            def materialize(self, place=None):
                if self.place is not None:
                    return self.place.materialize(place)
                lhs = make_temp()
                self.left.materialize(lhs)
                rhs = self.right.materialize()
                builder.add_statement('{} {}, {}'.format(self.op, lhs, rhs))
                self.place = lhs.materialize(place)
                return self.place

        class Atom(Expression):
            def __init__(self, value):
                self.value = value
            def __str__(self):
                return str(self.value)
            def materialize(self, place=None):
                if place is None or str(place) == str(self):
                    return self
                else:
                    builder.add_statement('MOV {}, {}'.format(place, self))
                    assert place is not None
                    return place
            @staticmethod
            def from_addr(addr):
                if addr in range(256):
                    return Atom('[{}]'.format(addr))
                elif addr in list('abcdefgh'):
                    return Atom(addr)
                else:
                    assert False, addr

        class Mem(object):
            def __init__(self):
                self._next_attr = 200
                self._attrs = {}
            def __getitem__(self, addr):
                return Atom.from_addr(addr)
            def __setitem__(self, addr, rhs):
                dst = Atom.from_addr(addr)
                rhs = Expression.ensure(rhs)
                rhs.materialize(dst)
            def find_attr(self, name):
                if name in self._attrs:
                    return self._attrs[name]
                a = Atom.from_addr(self._next_attr)
                self._next_attr += 1
                self._attrs[name] = a
                builder.add_statement('; {} is {}'.format(name, a))
                return a
            def __getattr__(self, name):
                return self.find_attr(name)
            def __setattr__(self, name, value):
                if name.startswith('_'):
                    self.__dict__[name] = value
                else:
                    Expression.ensure(value).materialize(self.find_attr(name))

        def set_dir(dir):
            Expression.ensure(dir).materialize(mem['a'])
            self.inline('INT 0')

        def get_lm_coords():
            self.inline('INT 1')
            return mem['a'], mem['b']

        def get_index():
            self.inline('INT 3')
            return mem['a']

        def get_ghost_coords(index):
            Expression.ensure(index).materialize(mem['a'])
            self.inline('INT 5')
            return mem['a'], mem['b']

        mem = Mem()

        return dict(
            join=self.join,
            inline=self.inline,
            mem=mem,
            set_dir=set_dir,
            get_lm_coords=get_lm_coords,
            get_index=get_index,
            get_ghost_coords=get_ghost_coords,
        )

    def join(self):
        label = self.get_simple_label(skip=1)
        self.branch({None: label})

    def inline(self, cmd):
        self.add_statement(cmd)

    def get_ghc(self):
        result = []

        bbs = self.reverse_postorder()

        for i, bb in enumerate(bbs):
            result.append('{}:'.format(bb.label))
            for s in bb.statements:
                result.append('    {}'.format(s))
            if True in bb.next:
                assert False in bb.next
                assert len(bb.next) == 2
                assert '__jump_dst' in result[-1]
                result[-1] = result[-1].replace('__jump_dst', bb.next[True].label)
                if bbs[i + 1] is not bb.next[False]:
                    result.append('    JEQ {}, 0, 0'.format(bb.next[False].label))
            elif None in bb.next:
                assert len(bb.next) == 1
                if bbs[i + 1] is not bb.next[None]:
                    result.append('    JEQ {}, 0, 0'.format(bb.next[None].label))
            else:
                assert bb is self.end

        return ''.join(line + '\n' for line in result)

    def get_delabelized_ghc(self):
        return ''.join(
            line + '\n' for line in delabelize(self.get_ghc().splitlines()))


def main():
    def run():
        UP = 0
        RIGHT = 1
        DOWN = 2
        LEFT = 3

        mem.x, mem.y = get_ghost_coords(get_index())
        tx, ty = get_lm_coords()
        mem.dx = tx - mem.x
        mem.dy = ty - mem.y

        def abs(x):
            return x if x < 128 else 0 - x
        mem.adx = abs(mem.dx)
        mem.ady = abs(mem.dy)

        if mem.adx > mem.ady:
            if mem.dx < 128:
                set_dir(RIGHT)
            else:
                set_dir(LEFT)
        else:
            if mem.dy < 128:
                set_dir(DOWN)
            else:
                set_dir(UP)
        inline('HLT')

    builder = AghostBuilder()
    builder.explore(run)

    print builder.get_delabelized_ghc()


if __name__ == '__main__':
    main()
