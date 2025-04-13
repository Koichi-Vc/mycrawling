from logging import getLogger,INFO, DEBUG
from logging import StreamHandler


formatter = 'Debug logs. %(filename)s | %(funcName)s | %(lineno)d | %(message)s'

debug_logger = getLogger(__name__)
handler = StreamHandler()
handler.setFormatter(formatter)
debug_logger.addHandler(handler)
debug_logger.setLevel(INFO)

#debug_loggerとconfパッケージ間の循環インポート問題を次回解決する。
def get_debug_log(debug=False):
    global debug_logger
    #from mycrawling.conf.data_setting import ref_dataconfig
    
    if debug is True:
        debug_logger.setLevel(DEBUG)    
    return debug_logger


