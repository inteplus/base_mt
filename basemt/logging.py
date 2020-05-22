"""Customised logging"""

from mt.base import logger
logger.warn_module_move('basemt.logging', 'mt.base.logging')

from mt.base.logging import *
