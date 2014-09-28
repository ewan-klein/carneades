# Author: Eli Bendersky <eliben@gmail.com>
#         Ewan Klein <ewan@inf.ed.ac.uk> (modifications)
#
# License: in public domain
# See http://eli.thegreenplace.net/2012/08/22/easy-tracing-of-nested-function-calls-in-python

"""
Module to see what calls actually occurred during execution, their arguments
and return values, when executing algorithms with complex function call
sequences, and especially ones that require recursion.

The class :class:`TraceCalls` is called as a decorator :func:`@TraceCalls`.
"""
import sys
from functools import wraps
import logging

class TraceCalls(object):
    """ 
    Use as a decorator on functions that should be traced. Several functions
    can be decorated; they will all be indented according to their call
    depth.
        
    """
    def __init__(self, stream=sys.stdout, indent_step=2, show_ret=True):
        """
        :param stream: The output stream
        :param indent_step: How much to indent strings relative to call depth.
        :type indent_step: int
        :param show_ret: If ``True``, show the return value of the function call.
        """
        self.indent_step = indent_step
        self.show_ret = show_ret
        TraceCalls.cur_indent = 0
        self.stream = stream

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            indent = ' ' * TraceCalls.cur_indent
            argstr = ', '.join(
                [str(a) for a in args][1:])
            self.stream.write("\n{}Calling {}({})\n".format(indent, fn.__name__, argstr))

            TraceCalls.cur_indent += self.indent_step
            ret = fn(*args, **kwargs)
            TraceCalls.cur_indent -= self.indent_step

            if self.show_ret:
                self.stream.write("{}{}({})-->{}\n".format(indent, fn.__name__,
                                                      argstr, ret))
                return ret
        return wrapper