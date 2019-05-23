'''Wrapper around threading for running things in background.'''


import threading as _t
import sys as _sys
import base_mt.traceback as _tb

class BgException(Exception):

    def __init__(self, message, exc_info):
        lines = _tb.format_exception(*exc_info)
        lines = ["  "+x for x in lines]
        lines = [message, "{"] + lines + ["}"]
        message = '\n'.join(lines)
        super().__init__(message)


class BgInvoke(object):
    '''Thin wrapper around threading.Thread to run `target(*args, **kwargs)` in background.

    Once invoked, the thread keeps running in background until function `self.is_running()` returns `False`, at which point `self.result` holds the output of the invocation.
    
    If an exception was raised, `self.result` would contain the exception and other useful information.

    Examples
    --------
    >>> def slow_count(nbTimes=100000000):
    ...     cnt = 0
    ...     for i in range(nbTimes):
    ...         cnt = cnt+1
    ...     return cnt
    ...
    >>> from base_mt.bg_invoke import BgInvoke
    >>> from time import sleep
    >>> a = BgInvoke(slow_count, nbTimes=100000000)
    >>> while a.is_running():
    ...     sleep(0.5)
    ...
    >>> print(a.result)
    100000000
    '''

    def _wrapper(self, g, *args, **kwargs):
        try:
            self._result = g(*args, **kwargs)
        except Exception as e:
            self._result = _sys.exc_info()

    @property
    def result(self):
        if hasattr(self, '_result'):
            if isinstance(self._result, tuple) and issubclass(self._result[0], Exception): # an exception
                raise BgException("Exception raised in background thread {}".format(self.thread.ident), self._result)
            return self._result
        else:
            raise ValueError("Result is not available.")

    def __init__(self, target, *args, **kwargs):
        '''Initialises the invocation of `target(*args, **kwargs)` in background.

        Parameters
        ----------
            target : callable
                callable object to be invoked. Default to None, meaning nothing is called.
            args : tuple
                argument tuple for the target invocation. Default to ().
            kwargs : dict
                dictionary of keyword arguments for the target. Default to {}.
        '''
        self.thread = _t.Thread(target=self._wrapper, args=(target,)+args, kwargs=kwargs)
        self.thread.daemon = True
        self.thread.start()

    def is_running(self):
        '''Returns whether the invocation is still running.'''
        return self.thread.is_alive()

