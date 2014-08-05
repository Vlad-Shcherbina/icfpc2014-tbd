""" Control flow graph builder. """

import StringIO
import inspect


class BasicBlock(object):
    __slots__ = [
        'label',
        'statements',
        'next',
    ]
    def __init__(self, label):
        self.label = label
        self.statements = []
        self.next = {}


class ReachedNewBranchingPoint(Exception):
    def __init__(self, alternatives):
        self.alternatives = alternatives


class CfgBuilder(object):
    BEGIN_LABEL = '***begin***'
    END_LABEL = '***end***'

    def reverse_postorder(self):
        postorder = []
        visited = set()
        def rec(block):
            if block.label in visited:
                return
            visited.add(block.label)
            for k, v in sorted(block.next.items()):
                rec(v)
            postorder.append(block)
        rec(self.begin)
        assert len(postorder) == len(self.basic_blocks)
        assert postorder[0] == self.end
        assert postorder[-1] == self.begin
        return postorder[::-1]

    def get_stack(self):
        stack = inspect.stack()[1:]
        for i in range(len(stack)):
            if stack[i][0].f_code is self.explore.func_code:
                del stack[i:]
                return stack
        assert False, 'explore function not found in the stack'

    def get_simple_label(self, skip=0):
        result = []
        for frame in reversed(self.get_stack()[skip + 1:]):
            frame_info = inspect.getframeinfo(frame[0])
            result.append('{}:{}'.format(frame_info.function, frame_info.lineno))
        return '/'.join(result)

    def add_statement(self, statement):
        if not self.cur_path:
            # only record in the last block in the path
            self.current.statements.append(statement)

    def branch(self, alternatives):
        if self.cur_path:
            alternative = self.cur_path.pop(0)
            label = alternatives[alternative]
            self.current = self.basic_blocks[label]
            return alternative
        else:
            raise ReachedNewBranchingPoint(alternatives)

    def explore(self, f):
        old_globals = dict(f.func_globals)
        f.func_globals.update(self.faked_globals())


        self.begin = self.current = BasicBlock(self.BEGIN_LABEL)
        self.basic_blocks = {self.begin.label: self.begin}

        work_queue = [[]]
        while work_queue:
            path = work_queue.pop()
            self.cur_path = path[:]
            self.current = self.begin

            try:
                f()
                self.branch({None: self.END_LABEL})
                assert self.current.label == self.END_LABEL
                self.end = self.current
            except ReachedNewBranchingPoint as e:
                assert not self.current.next
                for alt, label in e.alternatives.items():
                    if label not in self.basic_blocks:
                        self.basic_blocks[label] = BasicBlock(label)
                        work_queue.append(path + [alt])
                    self.current.next[alt] = self.basic_blocks[label]

        f.func_globals.clear()
        f.func_globals.update(old_globals)

    def faked_globals(self):
        raise NotImplementedError()


class CfgBuilderDemo(CfgBuilder):
    def faked_globals(self):
        return dict(
            join=self.join,
            nondet=self.nondet,
            action=self.action)

    def action(self, action):
        label = self.get_simple_label(skip=1)
        self.add_statement('{} @ {}'.format(action, label))

    def join(self):
        label = self.get_simple_label(skip=1)
        self.branch({'goto': label})

    def nondet(self):
        label = self.get_simple_label(skip=1)
        self.branch({'goto': label + '-nondet'})
        self.add_statement('toss a coin')
        return self.branch({True: label + '-true', False: label + '-false'})

    def get_listing(self):
        out = StringIO.StringIO()

        bbs = self.reverse_postorder()
        for i, bb in enumerate(bbs):
            print>>out, '{}:'.format(bb.label)
            for s in bb.statements:
                print>>out, '    {}'.format(s)
            for k, v in sorted(bb.next.items(), reverse=True):
                if i + 1 < len(bbs) and bbs[i + 1] == v:
                    # goto next label is implied
                    continue
                print>>out, '    {} -> {}'.format(k, v.label)

        return out.getvalue()


def main():
    def f():
        if nondet():
            action('begin')
            while not nondet():
                action('loop')
            action('end')
        else:
            action('do nothing')

    builder = CfgBuilderDemo()
    builder.explore(f)
    print builder.get_listing()


if __name__ == '__main__':
    main()
