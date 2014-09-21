# Author: Eli Bendersky <eliben@gmail.com>
#         Ewan Klein <ewan@inf.ed.ac.uk> (modifications)
# 
# See http://eli.thegreenplace.net/2012/08/22/easy-tracing-of-nested-function-calls-in-python


import sys
from functools import wraps
import logging

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

class TraceCalls(object):
    """ 
    Use as a decorator on functions that should be traced. Several functions
    can be decorated - they will all be indented according to their call
    depth.
        
    """
    def __init__(self, indent_step=2, show_ret=True):
        self.indent_step = indent_step
        self.show_ret = show_ret
        TraceCalls.cur_indent = 0

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            indent = ' ' * TraceCalls.cur_indent
            argstr = ', '.join(
                [str(a) for a in args][1:])
            logging.debug("{}Calling {}({})".format(indent, fn.__name__, argstr))

            TraceCalls.cur_indent += self.indent_step
            ret = fn(*args, **kwargs)
            TraceCalls.cur_indent -= self.indent_step

            if self.show_ret:
                logging.debug("{}{}({})-->{}\n".format(indent, fn.__name__,
                                                      argstr, ret))
                return ret
        return wrapper