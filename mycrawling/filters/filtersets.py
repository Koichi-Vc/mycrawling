from typing import List, Dict
from mycrawling.utils.operators import SelectListOperator
from mycrawling.utils.method_parse import run_method
from mycrawling.logs.debug_log import debug_logger


#Var37.06.14.15a(24/07/25/時点のバージョン)
class Elements_Filterset(SelectListOperator):
    '''beautifulsoup.find, find_allに渡すフィルターセットを生成するクラス '''
    '''
    インスタンス化時にフィルターメソッドを保持しfind, find_allへ実際に渡す。
    <フィルターとしての使い方>
    インスタンス自体をフィルターとして使うか、又はelements_filtersメソッドをフィルターとして使う。
    
    '''

    def __init__(self, *filter_method_list, list_operator_type=any, custom_list_operator=None, **kwargs):
        '''
        self.filters: 予め用意したフィルターメソッドのリストをセットする。 
        当クラスのインスタンス化時にフィルターを追加する場合は、以下のパラメータに値を渡す
        ''' 
        #filter_methods: 1乃至複数の検索フィルターメソッドを渡す。
        #呼び出し可能なフィルターのみfiltersへ格納。内包表記が問題であればfor文で対応
        #self.filters = [method for method in filter_method_list if callable(method)]
        debug_logger.debug(f'filter_method_list: {filter_method_list}')
        
        self.filters = []
        if not custom_list_operator:
            self.list_operator = self.select_operator(list_operator_type)
        elif callable(custom_list_operator):
            self.list_operator= custom_list_operator

        for method in filter_method_list:
            if callable(method):
                self.filters.append(method)
        debug_logger.debug(f'filters: {self.filters}')


    def __call__(self, element):
        ''' 保持した全てのfilter_methodをelementに実行し結果リストを論理演算する。 '''
        #メソッドでは無くクラスインスタンスそのものを渡す場合に__call__が働く。
        result = False
        result_list = [f(element) for f in self.filters]
        #print(f'filtersetclass>> result_list: {result_list} | list_operator: {self.list_operator}')
        result = self.list_operator(result_list)
        return result

    def add_filter(self, filter_method):
        '''フィルターを追加する。'''
        if not callable(filter_method):
            raise TypeError(f'methodはフィルターとして機能しません。| {filter_method}')
        self.filters.append(filter_method)


    def elements_filters(self, element):
        ''' フィルターセットを実行。 '''
        result = False
        result_list = [f(element) for f in self.filters]
        result = self.list_operator(result_list)
        return result


    @classmethod
    def filterset_factory(cls, *filter_method_list, list_operator_type=any, custom_list_operator=None, **kwargs):
        ''' filtersetのインスタンスを生成する。 '''
        return cls(*filter_method_list, list_operator_type, custom_list_operator, **kwargs)
        

#Var37.06.14.15a(24/07/25/時点のバージョン)
def filterset_factory(createfilter_cls, filterset_cls= Elements_Filterset, createfilter_factory_param:List[Dict]=[dict()], **kwargs):
    #検索フィルタークラスのインスタンスを生成しフィルターセットに束ねる。
    '''
    対象(要素の属性等)を複数のフィルターを指定する。
    args:
        createfilter_cls:
            検索フィルターを作成するクラス
        filterset_cls:
            複数フィルターを束ねて一つのフィルターにするクラス
        createfilter_factory_param:
            createfilter_clsからフィルターインスタンスを生成する為の引数の辞書

    '''
    debug_logger.debug(f'createfilter_cls: {createfilter_cls} | filterset_cls: {filterset_cls}')
    debug_logger.debug(f'createfilter_factory_param: {createfilter_factory_param}')
    instance_list = []
    
    if isinstance(createfilter_factory_param, dict):
        createfilter_factory_param = [createfilter_factory_param]

    #elif isinstance(createfilter_factory_param, (list, tuple)) and any(not isinstance(param, dict) for param in createfilter_factory_param):
    #    raise TypeError('createfilter_factory_paramには、Dict型をアイテムに持つリストを渡して下さい') 
    
    if not callable(createfilter_cls) or not callable(filterset_cls):
        return instance_list

    for parametor in createfilter_factory_param:
        #debug_logger.debug(f'parametor:{parametor}')
        instance = run_method(parametor, createfilter_cls)#run_methodにインスタンス化を代行させてみる。24/12/03

        if hasattr(instance, 'get_filter_method'):
            instance = instance.get_filter_method()

        instance_list.append(instance)

    return filterset_cls(*instance_list, **kwargs)


