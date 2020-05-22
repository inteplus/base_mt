'''Useful functions dealing with paths.

MT-NOTE: For backward compatibility only. Use module `mt.base.net` instead.'''

from mt.base import logger
logger.warn_module_move('basemt.path', 'mt.base.path')

from mt.base.path import *
