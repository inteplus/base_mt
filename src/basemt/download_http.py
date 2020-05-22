'''Downloads from http with multiple connections'''

from mt.base import logger
logger.warn_module_move('basemt.download_http', 'mt.base.download_http')

from mt.base.download_http import *
