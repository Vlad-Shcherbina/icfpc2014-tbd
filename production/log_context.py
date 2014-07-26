"""
Nested contexts for log messages, kind of like NDC.

See http://forumbgz.ru/showflat.php?Cat=&Board=prog&Number=11890088
"""

import logging
import contextlib


INDENT = '  '


@contextlib.contextmanager
def log_context(msg, *args):
    name = 'log_context'
    level = 0
    fn = None
    lno = None
    exc_info = None
    func = None
    msg = INDENT * len(context_stack) + msg
    record = logging.LogRecord(name, level, fn, lno, msg, args, exc_info, func)

    context_stack.append(record)
    yield
    assert context_stack[-1] is record
    context_stack.pop()


def decorate_handlers(logger=None):
    """ Make all handlers of a given logger context-aware. """
    if logger is None:
        logger = logging.getLogger()
    handlers = list(logger.handlers)
    for h in handlers:
        logger.removeHandler(h)
        logger.addHandler(HandlerDecorator(h))


context_stack = []


class HandlerDecorator(object):
    def __init__(self, handler):
        self.handler = handler
        self.emitted_contexts = []

    @property
    def level(self):
        return self.handler.level

    def handle(self, record):
        if self.handler.filter(record):
            self.emit_contexts()
            old_msg = record.msg
            record.msg = INDENT * len(context_stack) + old_msg
            self.handler.emit(record)
            record.msg = old_msg

    def emit_contexts(self):
        del self.emitted_contexts[len(context_stack):]
        i = len(self.emitted_contexts)
        while i and self.emitted_contexts[i - 1] is not context_stack[i - 1]:
            i -= 1
        del self.emitted_contexts[i:]

        for ctx in context_stack[i:]:
            self.handler.emit(ctx)
            self.emitted_contexts.append(ctx)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)

    def process_wheel(wheel):
        logger.debug('processing wheel %s', wheel)
        if wheel in [6661, 6662, 8882]:
            logger.warning('problem with the wheel %s', wheel)
        if wheel == 9991:
            raise Exception('hz')

    def process_bicycle(bicycle):
        with log_context('bicycle %s', bicycle):
            for wheel in 10 * bicycle + 1, 10 * bicycle + 2:
                process_wheel(wheel)

    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)8s:%(name)15s: %(message)s')
    decorate_handlers()

    logger.info('hello')
    try:
        with log_context('process all bicycles'):
            for i in range(1000):
                process_bicycle(i)
    except:
        logger.exception('unhandled exception')
