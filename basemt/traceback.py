"""Traceback extra"""

import traceback as _tb
from traceback import *


def format_exc_info(exc_type, exc_value, exc_traceback):
    '''Formats (exception type, exception value, traceback) into multiple lines.'''
    statements = _tb.format_exception(exc_type, exc_value, exc_traceback)
    statements = "".join(statements)
    return statements.split('\n')
