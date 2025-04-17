import sys
import logging
from inspect import ismethod, isfunction
import traceback
from typing import Dict
from collections.abc import Iterable
from collections import deque
from mycrawling.utils.imports_module import get_module
from .debug_log import debug_logger

#Var37.06.14.15a(24/07/24/時点のバージョン)
class Errorloghandlings_Class:

    '''
    注意!: このクラスが対象として想定しているのは、クラスに属するメソッドです。グローバル空間上のメソッドに対しては予期しないエラーを返す可能性が有ります。

    此のクラスはデコレータとして機能し、発生した例外に対するログ出力及びUIへのテキストメッセージの出力を制御します。
        args:
            #エラー処理の一貫性の観点から見てcustom_message_dictは削除する方向で行く。
            custom_message_dict:
                例外に対するメッセージ、ログのカスタムを定義する。
                exceptionタイプ毎にテキストメッセージおよびログメッセージ、ログレベルを定義した辞書型として渡す。
                exceptoinオブジェクトはstr()で文字列化して渡す。
                書式:
                    {str(exceptiontype): {'textmessage':'ユーザーインターフェースへのメッセージ',
                                          'logmessage': 'ログメッセージ',
                                          'loglevel':int又は__loglevel_dictのキーを指定,
                                          }}

            catch_exception:
                bool型で渡す。初期値はFalse
                値:
                    False: sys.exc_info()を実行して例外を取得し、テキスト/ログ出力フローを実行する。
                    True: exc_type, exc_value, exc_tracebackを受け取り、テキスト/ログ出力フローを実行する。
                !注意!:
                    __exit__を始め、exc_type, exc_value, exc_tracebackを受け取るオブジェクトをデコレートする際には必ずTrueにしておく。
            
            conf_message_val:
                custom_message_dict未指定で、設定オブジェクト(ref_dataconfig)から例外処理定義を取得する際の設定変数名を指定する。
                
    '''

    __loglevel_dict = {
            'debug': 10,
            'info': 20,
            'warning': 30,
            'error': 40,
            'critical': 50
            }
    
    default_loglevel = 'warning'
    default_error_message_texts = ['予期しないトラブル・エラーが発生しました。']

    def __init__(self, logger=None, tb_detail_index_li='all', catch_exception=False, **kwargs):
        logger_conf_variable = kwargs.pop('logger_conf_variable', None)
        logger_conf = None
        if logger_conf_variable and isinstance(logger_conf_variable, str):
            logger_conf = self.get_setting_conf(logger_conf_variable)
        else:
            logger_conf = logger_conf_variable
        
        if logger_conf and logger:
            logger_conf['getlogger'] = logger

        if 'handler' in logger_conf and isinstance(logger_conf['handler'], str):
            logger_conf['handler'] = get_module(logger_conf['handler'])()

        self.error_logger = self.setup_logger(**logger_conf)
        #conf_message_val = kwargs.pop('conf_message_val', None)#
        #self.custom_message_dict = kwargs.pop('custom_message_dict', self.set_custom_messages(variable_name=conf_message_val))#exception別にUI及びログメッセージ内容を定義した辞書
        custom_message_dict = kwargs.get('custom_message_dict', dict())
        if isinstance(custom_message_dict, str) and custom_message_dict.isupper():
            self.custom_message_dict = self.set_custom_messages(custom_message_dict, self)
        else:
            self.custom_message_dict = custom_message_dict
        
        self.tb_detail_index_li = tb_detail_index_li
        self.message_list = []
        self.catch_exception = catch_exception#exc_infoを取得している場合True. __exit__に付ける場合に使用
        self.format_extra = kwargs.pop('format_extra', dict())


    def help(self):
        '''
        セットアップ:
                Errorloghandlings_Class.setup_logger()にロガー名とハンドラ、フォーマッター、ログ出力レベルを指定して実行する。
        例外発生時のテキスト及びログメッセージの内容を定義する:
                custom_message_dict引数に詳細なメッセージ内容と出力レベルを定義する。

                custom_message_dictのセット方法:
                    Errorloghandlings_Classのインスタンス変数に定義出来る他、get_exc_handling_variable.wrapperで対象のインスタンス(instance_obj)
                    からも取得を試みる為、デコレートするメソッドのインスタンス変数にself.custom_message_dictを定義しても適用される。

        '''
        return
    
    #25/02/15/新規追加。設定ファイルにカスタムエラーメッセージを定義してインポートする。
    #この場合、キーが例外オブジェクトのパスだった場合インポートする必要がある為インポートのロジックを次回以降考える。
    
    @classmethod
    def get_setting_conf(cls, variable_name=None):
        from mycrawling.conf.data_setting import ref_dataconfig
        if variable_name:
            settings_conf = ref_dataconfig.get_conf_value(variable_name)
        else:
            settings_conf = None
        return settings_conf


    @classmethod
    def set_custom_messages(cls, message_conf_name=None, instance=None):
        ''' 設定オブジェクト(ref_dataconfig)に定義されているカスタムエラーメッセージ情報を取得する。'''

        custom_message_dict = cls.get_setting_conf(variable_name=message_conf_name)

        for exception_type in custom_message_dict.copy():
            if isinstance(exception_type, str):
                #キーが文字列だった場合、例外クラスのインポートパスと解釈してインポートを試みる。
                exception_obj = get_module(exception_type)
                custom_message_dict[exception_obj] = custom_message_dict.get(exception_type)
            
            elif not issubclass(exception_type, Exception):
                raise TypeError(f'対応していない例外オブジェクトです。exception_type: {exception_type}')
        if instance and isinstance(instance, cls):
            instance.custom_message_dict = custom_message_dict
            return instance.custom_message_dict
        
        return custom_message_dict

    
    #get_exc_handling_variable改良ver2
    def format_exc_handling_variagle(self, instance_obj, **kwargs):
        ''' ログ出力前のパラメータを引数から受けとった場合は、セットを行う。 '''
        
        if hasattr(instance_obj, 'error_logger'):
            self.error_logger = getattr(instance_obj, 'error_logger')
        if hasattr(instance_obj, 'custom_message_dict') and instance_obj.custom_message_dict:
            self.custom_message_dict = instance_obj.custom_message_dict
        
        if hasattr(instance_obj, 'tb_detail_index_li'):
            self.tb_detail_index_li = instance_obj.tb_detail_index_li
        
        self.log_save = getattr(instance_obj, 'log_save', True)
        if hasattr(instance_obj, 'format_extra'):
            self.format_extra = getattr(instance_obj, 'format_extra')
         


    def __call__(self, method):
        methods_instance = None
        is_function = isfunction(method)
        is_bound_method = ismethod(method)
        if is_bound_method:
            methods_instance = self.get_methods_instance(method)

        def wrapper(instance_obj, *args, **kwargs):
            debug_logger.debug(f'instance_obj: {instance_obj}')
            debug_logger.debug(f'self: {self}')
            debug_logger.debug(f'args: {args}')
            debug_logger.debug(f'kwargs: {kwargs}')
            args_list = list()

            if is_bound_method and methods_instance:
                #
                args_list = list(args)
                args_list.insert(0, instance_obj)
                instance_obj = methods_instance
            else:
                args_list = args
            self.format_exc_handling_variagle(instance_obj, **kwargs)

            tb_detail_index_li = self.tb_detail_index_li
            log_save = self.log_save
            
            try:
                if is_function:
                    return method(instance_obj, *args_list, **kwargs)
                else:
                    return method(*args_list, **kwargs)
                
            except Exception:
                exc_type, exc_value, exc_tb = sys.exc_info()
                error_logger = self.error_logger
                error_text = self.error_handling(error_logger, exc_type, exc_value, exc_tb, log_save, tb_detail_index_li)
                setattr(instance_obj, 'error_message', error_text)
                debug_logger.debug(f'error_logger: {error_logger} | error_text: {error_text}')

        
        def wrapper_catch_except(instance_obj=None, *exc_objcts, **exc_obj_kwgs):

            if is_bound_method and methods_instance:
                instance_obj = methods_instance
            self.format_exc_handling_variagle(instance_obj)

            error_logger = self.error_logger
            exc_obj_kwgs['custom_message_dict'] = self.custom_message_dict
            exc_obj_kwgs['tb_detail_index_li'] = self.tb_detail_index_li
            exc_obj_kwgs['log_save'] = self.log_save

            if exc_objcts or exc_obj_kwgs:
                error_text = self.error_handling(error_logger, *exc_objcts, **exc_obj_kwgs)
                setattr(instance_obj, 'error_message', error_text)

            return method(instance_obj, *exc_objcts)

        if self.catch_exception is True:
            return wrapper_catch_except
        return wrapper 

    #add_error_text,add_error_text_betaメソッドの存在意義が薄れた為別の機能として実装してみる
    def join_error_text_beta(self,*messages, separator=' | '):
        ''' エラーに対する複数のテキスト/ログメッセージをseparatorで結合する。 '''
        join_message = ''
        for message in messages:
            join_message += message
            join_message += separator
        return join_message

    @classmethod
    def get_methods_instance(cls, method):
        ''' methodからインスタンスオブジェクトを参照,取得する。
        インスタンスオブジェクトが取得出来ないかグローバル関数等である場合はNoneを返す。
        '''
        result = None
        is_bound_method = ismethod(method)
        if is_bound_method and hasattr(method, '__self__'):
            result = method.__self__
        return result

    @classmethod
    def set_formatter(cls, formatter=None):
        ''' フォーマッタの定義 '''
        if not formatter:
            #formatterを指定しない場合、以下のフォーマッタがデフォルトでセットされる。
            formatter = '%(asctime)s | %(created)s | %(name)s | %(levelname)s | %(message)s | '
        fmt = logging.Formatter(formatter)

        return fmt


    @classmethod
    def set_handler(cls, logger, handler, formatter=None, howmany_handlers:'許容するハンドラ数'=1,**kwargs):
        '''ロガーのハンドラを指定してセットする  '''
        if not isinstance(formatter, logging.Formatter):
            formatter = cls.set_formatter(formatter)
        
        handler.setFormatter(formatter)
        length_handlers = len(logger.handlers)

        if length_handlers < howmany_handlers:
            #ハンドラ数が指定数以内ならセット。
            logger.addHandler(handler)
        elif length_handlers > howmany_handlers:
            no_delete_handler_type = kwargs.get('no_delete_handler_type', None)
            logger = cls.remove_handlers(logger, howmany_handlers, no_delete_handler_type)
        return logger


    @classmethod
    def remove_handlers(self, logger, howmany_handlers:'保持するハンドラ数'= 1, no_delete_handler_type:'削除しないハンドラタイプ'=None):
        ''' 不要なハンドラを削除する※ 現在使う用途が無いが機能はすると思う。24/02/22'''

        is_iterable = isinstance(no_delete_handler_type, Iterable)
        if no_delete_handler_type and not is_iterable:
            no_delete_handler_type = set(no_delete_handler_type)

        for handler in logger.handlers[:]:

            if no_delete_handler_type and isinstance(handler, no_delete_handler_type):
                #削除しないハンドラタイプ
                continue

            elif len(logger.handlers) > howmany_handlers:
                logger.removeHandler(handler)
            else:
                break
        return logger


    @classmethod
    def setup_logger(cls, getlogger=None, handler=None, **kwargs):
        ''' ロガーの取得とセットアップ '''
        debug_logger.debug(f'cls: {cls} |getlogger:{getlogger} | handler: {handler} | kwargs:{kwargs}')
        
        fmt = None

        if isinstance(getlogger, str):
            logger = logging.getLogger(getlogger)
        elif isinstance(getlogger, logging.Logger):
            logger = getlogger
        else:
            logger = logging.getLogger('Error_logs')

        fmt = kwargs.pop('formatter', None)
        
        formatter = cls.set_formatter(fmt)
        if not handler:
            handler = logging.StreamHandler()
        logger = cls.set_handler(logger, handler, formatter, **kwargs)

        if 'level' in kwargs:
            level = kwargs.pop('level')
            logger.setLevel(level=level)
        
        return logger 


    def output_select(cls,select_loglevel):
        ''' ログ出力レベルの指定 '''
        output_level = 30#指定したログレベルが無い場合常に30を返す。

        if isinstance(select_loglevel, str) and select_loglevel in cls.__loglevel_dict:
            ''' 指定したログレベル(str型)がキーに含まれていたら返す '''
            output_level = cls.__loglevel_dict[select_loglevel]
        elif isinstance(select_loglevel, int) and select_loglevel in cls.__loglevel_dict.values():
            ''' 指定したログレベル(整数値)が値に含まれていたら返す。 '''
            output_level = select_loglevel
        return output_level

    
    def output_exc_message(self,
                         logger,
                         exc_type,
                         exc_value,
                         exc_tb_detail,
                         custom_message_dict:Dict= None,
                         save=False,
                         ):
        
        ''' exceptionに定義されたエラーメッセージの記録と保存を実行。 '''
        output_level = 30
        log_text = ''
        error_message_texts = getattr(self, 'error_message_texts') if hasattr(self, 'error_message_texts') else self.default_error_message_texts
        
        if custom_message_dict is None:
            custom_message_dict = self.custom_message_dict
        
        debug_logger.debug(f'exc_type: {exc_type} | custom_message_dict: {custom_message_dict} | exc_type in custom_message_dict: {exc_type in custom_message_dict.keys()}')

        if custom_message_dict and exc_type in custom_message_dict.keys():

            custom_item = custom_message_dict.get(exc_type)
            error_messages = custom_item.get('textmessage', error_message_texts)
            
            if isinstance(error_messages, str):
                error_messages = [error_messages]
            debug_logger.debug(f'if True, error_messages:{error_messages}')

            logmessage_value = custom_item.get('logmessage', '')#ログメッセージを取得
            
            if isinstance(logmessage_value, Iterable) and not isinstance(logmessage_value, str):
                join_message = self.join_error_text_beta(*logmessage_value)
                log_text = join_message
            else:
                log_text = logmessage_value
            
            loglevel = custom_item.get('loglevel', self.default_loglevel)
            output_level = self.output_select(loglevel)

        else:
            error_messages = error_message_texts            

        debug_logger.debug(f'error_messages:{error_messages}')

        if save:
            message = f'{exc_type} | {exc_value} | {exc_tb_detail} | '
            if log_text:#ログ時に追加でテキストメッセージを指定している場合は追加する
                message += log_text
            debug_logger.debug(f'format_extra: {self.format_extra}')
            logger.log(output_level, message, extra=self.format_extra)#ここでログファイルへの出力処理をする
        
        return error_messages


    def rendering_traceback(self, tb_detail_index, *exc_info, **kwargs):
        ''' トレースバックの抽出とレンダリング実行。 '''
        
        formated_traceback_details = traceback.format_exception(*exc_info)
        #traceback_details_ext_list = []#トレースバックをインデックス又はスライスで収集
        extraction_traceback_details = []
        traceback_details = None
        if tb_detail_index == 'all':
            traceback_details = ''.join(formated_traceback_details).strip()
            return traceback_details
        
        if isinstance(tb_detail_index, str):
            tb_detail_index = [tb_detail_index]
        for tb_dt in tb_detail_index:
            traceback_text = ''
            
            if isinstance(tb_dt, int) and len(formated_traceback_details) <= tb_dt:
                traceback_text = formated_traceback_details[tb_dt]

            elif isinstance(tb_dt, (tuple, list, deque)):
                ''' リスト又はタプルを始めとするコレクション型の場合はスライスと解釈。
                 ※アイテム一つのみだった場合所謂[start:]又は[:end]と解釈 '''
                start, end, step = None, None, None
                if len(tb_dt) ==1:
                    start = tb_dt[0]
                elif len(tb_dt) == 2:
                    start, end = tb_dt
                elif len(tb_dt) == 3:
                    start, end, step = tb_dt

                traceback_text = formated_traceback_details[start:end:step]
            
            if isinstance(traceback_text, list):
                for tb_txt in traceback_text:
                    if tb_txt not in extraction_traceback_details:
                        extraction_traceback_details.append(tb_txt)

            elif traceback_text not in extraction_traceback_details:
                extraction_traceback_details.append(traceback_text)
        
        traceback_details = ''.join(extraction_traceback_details).strip()
        return traceback_details


    def error_handling(self,
                       logger,
                       exc_type,
                       exc_value,
                       exc_tb,
                       save=False,
                       tb_detail_index_li: "len( [int or 'all' or ('start', 'end')] )" == 2 = 'all',
                       **kwargs):
        
        ''' tb_detail_index_liはlist型で3アイテム以内のint、all、tuple('start','end')のスライスを想定します。 '''
        exc_info = []
        if exc_type:
            exc_info = [exc_type, exc_value, exc_tb]
        else:
            exc_info = sys.exc_info()

        traceback_details = self.rendering_traceback(tb_detail_index_li, *exc_info) 
        
        errer_message = self.output_exc_message(
            logger=logger,
            exc_type=exc_type,
            exc_value=exc_value,
            exc_tb_detail=traceback_details,
            save=save,
            **kwargs
            )
        
        debug_logger.debug(traceback_details)#コンソールへの出力を再現
        return errer_message

