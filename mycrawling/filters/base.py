from abc import ABC
from abc import abstractmethod
from mycrawling.logs.debug_log import debug_logger

#Var37.06.14.15a(24/07/25/時点のバージョン)
class AbstractElementsFilter(ABC):
    ''' 要素の属性名と属性値のフィルター '''
    def __init__(self,filter_method=None):
        debug_logger.debug(f'filter_method is callable: {callable(filter_method)}')
        self._filter_method = filter_method if callable(filter_method)else self.set_filter_method(filter_method) 


    """
    def __call__(self, element):
        #クラス自信がフィルタとして機能する。
        result = False
        result = self.__filter_function(element)
        return result
    """
    
    '''#__call__を使えばクラスをメソッドの様に呼び出せるが、
       #何を返すのか事前に把握し難い為get_filter_methodに代行させる。
    def __call__(self):
        #フィルターを作成して返す。
        created_filter = self.__filter_function
        return created_filter
    '''

    
    def set_filter_method(self, filter_name=None):
        ''' __call__で呼び出すフィルターをセットする '''
        
        filter_method = None

        if callable(filter_name):
            filter_method = filter_name

        elif isinstance(filter_name, str) and hasattr(self, filter_name):
            method = getattr(self, filter_name)
            is_method = callable(method)
            filter_method = method if is_method else None
            
        elif isinstance(filter_method, str) and not hasattr(self, filter_name):
            raise AttributeError(f'指定したフィルターメソッドはインスタンス内に存在しません。| instance: {self} | method: {filter_name}')
        
        if filter_method is None:
            self._filter_method = self.valuefilter
        else:
            self._filter_method = filter_method
        return self._filter_method


    #検索フィルターを取得するメソッド
    def get_filter_method(self):
        '''検索フィルターを取得する。 '''
        return self._filter_method


    @abstractmethod
    def valuefilter(self, element_attr):
        #属性値のみへ条件指定フィルターを定義。
        #属性名は別途引数や辞書のキーで定義されている事が前提。
        pass

    def values_listfilter(self, element_attr):
        ''' 属性名に対して複数属性値をフィルタリング候補に用いる場合に定義 '''
        pass


