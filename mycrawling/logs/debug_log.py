from logging import getLogger, DEBUG
from logging import Logger, StreamHandler, Formatter


debug_logger = getLogger(__name__)

def setting_debug_log(debug=False, formatter=None, logger=None, handler=None, **kwargs):
    global debug_logger

    propagate = kwargs.get('propagate', False)
    if not formatter:
        formatter = Formatter('Debug logs:  %(filename)s | %(funcName)s | %(lineno)d | %(message)s')
    if logger and isinstance(logger, Logger):
        debug_logger = logger
    elif isinstance(logger , str):
        debug_logger = getLogger(logger)
    
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
    debug_logger.propagate = propagate
    return debug_logger

def get_debug_logger():

    return debug_logger

def output_logger(debug_logger, loglevel=10, message=None, *args, **kwargs):
    stacklevel = kwargs.pop('stacklevel', 3)
    return debug_logger.log(loglevel, message, stacklevel=stacklevel, *args, **kwargs)

def retain_logs(logger_obj):
    ''' メッセージを一定の間蓄積し、出力する。'''
    '''
    do_record_log: ログ出力を実行する。Falseの場合は実行しない。
    insert_index: メッセージをメッセージリストの所定の位置に挿入するためのインデックスを指定する。デフォルトではNoneで末尾へ追加。
    refresh_messages: メッセージリストの内容をクリアする。
    '''
    logger_level = logger_obj.level
    messages = []
    
    def wrapper(loglevel=10, message=None, *args, **kwargs):
        nonlocal messages
        do_record_log = kwargs.pop('do_record_log', False)
        insert_index = kwargs.pop('insert_index', None)#ログメッセージを挿入する位置を指定。Noneの場合は末尾に追加。
        refresh_messages = kwargs.pop('refresh_messages', False)
        
        if refresh_messages is True:
            messages = []
            return 
        
        if logger_level == 0 or loglevel < logger_level:
            return
        
        if do_record_log is True:

            if message is not None and insert_index is not None:
                messages.insert(insert_index, message)
            elif message is not None:
                messages.append(message)
            
            return output_logger(logger_obj, loglevel, messages, *args, **kwargs)

        elif do_record_log is True and messages:
            return output_logger(logger_obj, loglevel, messages, *args, **kwargs)

        elif do_record_log is True and message:
            return output_logger(logger_obj, loglevel, message, *args, **kwargs)
        
        if message and insert_index is not None:
            messages.insert(insert_index, message)
        elif message:
            messages.append(message)
        
    return wrapper

