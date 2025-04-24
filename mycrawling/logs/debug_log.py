from logging import getLogger, DEBUG
from logging import StreamHandler, Formatter


debug_logger = getLogger(__name__)

def setting_debug_log(debug=False, formatter=None, logger=None, handler=None, **kwargs):
    global debug_logger

    if not formatter:
        formatter = Formatter('Debug logs:  %(filename)s | %(funcName)s | %(lineno)d | %(message)s')
    if logger:
        debug_logger = logger
    
    if not handler:
        handler = StreamHandler()
        handler.setFormatter(formatter)
    if debug is True:
        handler.setLevel(DEBUG)
        debug_logger.setLevel(DEBUG)

    if debug_logger.handlers:
        for handler in debug_logger.handlers[:]:
            debug_logger.removeHandler(handler)
    debug_logger.addHandler(handler)
    return debug_logger

def get_debug_logger():

    return debug_logger


