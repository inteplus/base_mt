'''Wrapper around threading for running things in background.'''

from mt.base import logger
logger.warn_module_move('basemt.bg_invoke', 'mt.base.bg_invoke')

from mt.base.bg_invoke import *
