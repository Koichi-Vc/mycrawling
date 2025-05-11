from inspect import isfunction, ismethod
import operator
from typing import List
from .base import AbstractElementsFilter
from mycrawling.logs.debug_log import debug_logger
from mycrawling.utils.method_parse import edit_keyword_argument
from mycrawling.utils.method_parse import run_method, method_parameter_parse, has_param_names
from mycrawling.utils.operators import SelectListOperator


#フィルター前後処理を定義するデコレータをクラスデコレータ版にしてみた。
class Processing():
    '''
    要素又は値をフィルターで評価する前後にプロセス(処理や加工)を追加する。 デフォルトでは何もしない(affix == no_process)
    になっている。
    
    '''

    def __init__(self, *affix_methods, affix=None, **kwargs):

        self.affix_methods = list(affix_methods) 
        self.affix = affix
        for kwg in kwargs:
            setattr(self, kwg, kwargs[kwg])
        self._instance_obj = None
        self.method = None


    def __call__(self, method):
        self.method = method#現状まだ役割として機能していない。

        return self.process(self.method)

    @property
    def instance_obj(self):
        return self._instance_obj
    
    @instance_obj.setter
    def instance_obj(self, instance):
        ''' テスト実装'''
        if hasattr(self, 'instance_obj'):
            self._instance_obj = None
        self._instance_obj = instance

  
    def _processing(self, *args_tup:List, instance=None, **kwargs):

        result = None
        first = True
        args_list = list(args_tup)
        args_list.append(kwargs)
        argument = args_list
        debug_logger.debug(f'args_tup: {args_tup} | affix_method: {self.affix_methods} | args_list: {args_list}')
        
        for affix_method in self.affix_methods:

            if isinstance(affix_method, str) and instance and hasattr(instance, affix_method):
                affix_method = getattr(instance, affix_method)
            if not callable(affix_method):
                continue

            debug_logger.debug(f'affix_method: {affix_method} | affix_method.__name__: {affix_method.__name__}')
            ''' ここのロジックで引数に渡すのがうまく行っていない為次回検証する。24/11/15/425'''
            if first is True:
                result = run_method(argument, affix_method)
                first = False
                debug_logger.debug(f'first is True. result: {result}')         
            else:
                result = run_method(result, affix_method)
        return result


    def process(self, method):
        ''' デコレータのラッパーメソッドを指定する。 '''

        has_self_parm = has_param_names(method_parameter_parse(method), 'self')#引数selfが定義されているかどうか。
        is_function = isfunction(method)#メソッドがグローバル又は、アンバウンドメソッドかどうかの判定。
        is_method = ismethod(method)
        debug_logger.debug(f'self: {self} | method: {method} | method_name: {method.__name__}')        
        debug_logger.debug(f'is_function: {is_function} | ismethod: {is_method} | has_self_param: {has_self_parm} ')

        def wrapper(*args, **kwargs):
            args_list = list(args)
            importance_keys = list()
            instance_obj = None

            debug_logger.debug(f'args: {args} | kwargs: {kwargs}')
            preprocess_args = list()#前処理に渡す引数を保持する。
            #methodがインスタンス化されていないインスタンスメソッドかを調べる
            if has_self_parm and is_function and not is_method:
                #selfが引数として定義され、グローバル関数判定され、且つインスタンスメソッドではない場合、アンバウンドなインスタンスメソッドであると判断。
                preprocess_args += args[1:]
                instance_obj = args_list[0]#一旦ここでインスタンスを抜き取る。

            elif self.instance_obj:
                instance_obj = self.instance_obj
                
            if not preprocess_args and args:
                preprocess_args = list(args)

            debug_logger.debug(f'preprocess_args: {preprocess_args} | instance_obj: {instance_obj}')
            debug_logger.debug(f'affix: {self.affix}')
            if self.affix == 'pre':
                debug_logger.debug('affix is pre')
                preprocessed = self._processing(*preprocess_args, instance=instance_obj, **kwargs)
                if instance_obj and has_self_parm:
                    '''
                    <ここでselfをキーワード引数に>
                    '''
                    preprocessed = edit_keyword_argument(preprocessed, {'self':instance_obj})
                    importance_keys.append('self')#位置引数として優先する。

                debug_logger.debug(f'preprocessed: {preprocessed}')
                return run_method(preprocessed, method, importance_keys=importance_keys)
            
            elif self.affix == 'after':
                debug_logger.debug(f'affix is after')
                debug_logger.debug(f'args_list: {args_list} | method: {method}')
                after_processed = run_method(args_list, method)
                #return self._processing(*after_processed, instance=instance_obj)
                after_processed = edit_keyword_argument(after_processed, {'instance': instance_obj})
                return run_method(after_processed, self._processing)
            if kwargs:
                #return method(instance, item, **kwargs) if instance else method(item, **kwargs)
                return run_method(args_list, method, importance_keys=importance_keys)

        return wrapper


#Var37.06.14.15a(24/07/25/1:24am時点のバージョン)
class ElementsFilter(AbstractElementsFilter, SelectListOperator):
    affix_methods = list()
    ''' 要素を属性でフィルタリングする '''
    
    def __init__(self, attr, criteria_value, condition= operator.eq, list_operator_type=any, filter_method=None, **kwargs):
        debug_logger.debug(f'kwargs:{kwargs} | filter_method: {filter_method}')
        self.attr = attr
        self.criteria_value = criteria_value
        self.values_list = kwargs.pop('values_list', list())#複数属性値を対象にする場合に指定
        self.condition = condition if callable(condition) else operator.eq
        self.list_operator = self.select_operator(list_operator_type)
                
        super().__init__(filter_method)


    def get_attribute(self, element):
        ''' 要素から指定した属性を取得する。値の場合はそのまま返される。 '''

        attr_value = None
        if hasattr(element, 'get'):
            attr_value = element.get(self.attr)

        elif self.attr and hasattr(element, self.attr):
            attr_value = getattr(element, self.attr)

        else:
            attr_value = element
        debug_logger.debug(f'element: {element} | attr_vlaue: {attr_value}')
        return attr_value        

    
    def invert_operand(self, element):
        #被演算子を反転する。
        attr_value = self.get_attribute(element)
        return self.criteria_value, attr_value


    def valuefilter(self, element, criteria_value=None):
        '''
        element:
            フィルター対象のアイテム
        criteria_value:
            評価する際の基準とする値。比較対象。
        '''
        elem_attr_value = self.get_attribute(element)
        debug_logger.debug(f'criteria_value: {criteria_value} | attr_value: {elem_attr_value}')
        if criteria_value is None:
            criteria_value = self.criteria_value        
        return self.condition(elem_attr_value, criteria_value)


    def values_listfilter(self, element_attr_value):
        ''' 属性値(属性値だけとは限らない)と複数の値リストを比較する '''
        return self.list_operator(element_attr_value == value for value in self.values_list)


    def customfilter(self, element_obj):
        ''' カスタムでフィルター関数を作成する場合に用いる'''
        pass


    @classmethod
    def filters_factory(cls, *args, **kwargs):
        return cls(*args, **kwargs)


