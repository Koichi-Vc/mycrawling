from typing import Dict
#from collections.abc import Iterable
#from inspect import signature
#from mycrawling.conf.data_setting import setting_conf
from mycrawling.filters.filtersets import filterset_factory
from mycrawling.filters.filtermanage import BaseFilterManage
#from .load_parameter_files import elements_filter_parameters, get_filter_parameters, FilterParameterLoader
from .load_parameter_files import FilterParameterLoader
from mycrawling.utils.method_parse import run_method, isiterable
from mycrawling.utils.loaders.loader import json_load
import logging
from mycrawling.logs.debug_log import debug_logger


filtermanage_object = None#必要かどうか現時点では不明。
filter_object = None#必要かどうか現時点では不明。

#parameter_files\elements_filter_arguments3.jsonを元に設計する。
class SearchElementFilterManager(BaseFilterManage):
    '''
    フィルタークラスとパラメータのインスタンス化を行う。
    フィルタークラスには、フィルターを取得する為のget_filter_methodが実装されている必要がある。__call__メソッドが定義されている場合はその
    限りでは無い。
    '''

    def __init__(self, *select_class_keys, filterset_cls=None, filter_parameters:Dict=None, **kwargs):

        self.createfilter_cls_obj_dict = self.get_createfilter_classes(*select_class_keys)#フィルター作成クラスを取得する。
        self.filterset_cls_obj = None
        self.filterset_cls = filterset_cls if filterset_cls else self.get_filterset_cls()
        
        self.retain_tag = set()#既に登録済みのタグ。Noneもタグ無しと言う意味で含める。
        is_load_files = kwargs.pop('is_load_files', True)#ファイルの読み込み許可。
        debug_logger.debug(f'not filter_parameters and not no_load_files: {not filter_parameters and not is_load_files}')
        encoding = kwargs.pop('encoding', 'UTF-8')
        #パラメータを取得する。新コード
        if not filter_parameters and is_load_files:
            self.filter_parameters = FilterParameterLoader.file_load(load_method= json_load, encoding=encoding)
        elif isinstance(filter_parameters, FilterParameterLoader) and is_load_files:
            self.filter_parameters = getattr(filter_parameters, 'elements_filter_parameters', dict())
        elif is_load_files:
            self.filter_parameters = dict()
        else:
            raise TypeError(f"filter_parametersが非サポートのデータ型を受けとりました | {filter_parameters}")

        #self.tag_filters = dict()#タグ(未指定もNoneとしてふくむ)に対するフィルター
        #self.query_filterset = dict()#ターゲットをキー、フィルターオブジェクトをアイテムとした辞書型。
        #filter_instance_obj_dictと名されているが、executable_filterの実装に伴い実態はフィルターオブジェクトを格納している。
        #その為、近日中に名称を変更する。
        self.filter_instance_obj_dict = dict()#タグ別(タグ未指定の場合、キーはNone)に生成したフィルターを格納。


    def select_filtercls_and_params(method):
        ''' インスタンスに登録済みのフィルターを作成する為のクラスと、パラメータを指定して取得する。'''

        def wrapper(self, tag_name,*args, **kwargs):
            '''
            tag_nameはタグ名によるフィルタークラスを取得する。
            '''
            createfilter_cls_obj = self.createfilter_cls_obj_dict.get(tag_name, None)
            createfilter_arguments = self.filter_parameters.get(tag_name, None)#クラス名(又はタグ名等)を指定して引数を取得。

            if not createfilter_cls_obj:
                raise KeyError(f'フィルタークラスが見つかりません。| tag_name:{tag_name}')

            return method(self, *createfilter_arguments, createfilter_cls=createfilter_cls_obj, tag_name=tag_name, **kwargs)
        return wrapper
    

    def create_element_filter(self, arguments,createfilter_cls, **kwargs):
        ''' 要素全体に対するフィルターを取得する。これで生成されるフィルターはBeautifulsoup.find_allの第一引数に渡される
        事を想定している。
        '''
        element_filter = self.filter_instantiation(arguments, createfilter_cls=createfilter_cls, **kwargs)
        filter_obj = self.executable_filter(element_filter)
        return filter_obj
    

    @select_filtercls_and_params
    def create_attrs_filters(self, *targets, createfilter_cls, **kwargs):
        ''' htmlタグの属性に対するフィルターを生成。'''
        '''
            targets:
                フィルター生成クラスをインスタンス化する為の引数データを保持しているキーを指定する。
                targetにはタグ名か又はクラス名を想定している。
        '''
        tag_name = kwargs.pop('tag_name', None)
        if tag_name not in self.filter_instance_obj_dict:
            self.filter_instance_obj_dict.setdefault(tag_name, dict())

        filter_instance_dict = {}
        first_print = False
        for target in targets:
            if not first_print:
                debug_logger.debug('create_attrs_filtersのループ内:')
                first_print = True
            debug_logger.debug(f'ループ,target: {target}')
            if isinstance(target, dict) and 'attr' in target and 'arguments' in target:
                attr = target.get('attr')if target.get('attr', None) else 'class'#attrキーがNoneの場合、クラス属性に対する指定とする。
                arguments = target.get('arguments')
                kwargs.setdefault('createfilter_cls', createfilter_cls)
                args = arguments

                if isiterable(arguments) and not isinstance(arguments,list):
                    args = list(arguments)
                elif not isiterable(arguments):
                    args = [arguments]
                
                args.append(kwargs)
                debug_logger.debug(f'ループ,\narguments: {arguments} \nargs: {args}')

                filter_instance = run_method(args, self.filter_instantiation)
                filter_obj = self.executable_filter(filter_instance)
                filter_instance_dict.setdefault(attr, filter_obj)

        self.filter_instance_obj_dict[tag_name].update(filter_instance_dict)


    def executable_filter(self, obj, **kwargs):
        ''' インスタンスがフィルターとして実行可能か評価する。Falseだった場合フィルターの取得を試みる。'''
        ''' もし実行可能なフィルター取得に失敗した場合は警告ログを出力する。'''
        if callable(obj):
            filter_obj = obj
        elif not callable(obj) and hasattr(obj, 'get_filter_method'):
            #そのままでフィルターとして実行出来ない場合インスタンスからフィルターの取得を試みる。
            filter_obj = obj.get_filter_method()
        else:
            filter_obj = obj
            logging.warning('インスタンスからフィルターを取得してください。')        
        return filter_obj
    

    def filter_instantiation(self,*arguments, createfilter_cls, **kwargs):
        ''' フィルター生成クラスにargumentsに格納されているパラメータを使ってインスタンス化を行う。'''
        ''' 
        argumentsが複数のパラメータのリストになっていた場合、一つの属性又はelementオブジェクトに対して複数のフィルターを生成
        すると言う事の為フィルターセットを作成する。
        '''
        debug_logger.debug(f'arguments: {arguments}')
        debug_logger.debug(f'createfilter_cls: {createfilter_cls}')
        debug_logger.debug(f'kwargs: {kwargs}')
        single_item = 1
        if arguments and len(arguments) == single_item:
            argument = arguments[0]
            debug_logger.debug('filter_instantiationのif節-------')
            return run_method(argument, createfilter_cls)

        filter_set = filterset_factory(createfilter_cls, self.filterset_cls, arguments, **kwargs)
        debug_logger.debug(f'filterset: {filter_set}')
        return filter_set


    def get_filter_instance(self, tag_name, **kwargs):
        ''' インスタンス化したフィルターオブジェクトを指定して取得する。 '''
        debug_logger.debug(f'tag_name: {tag_name} | kwargs: {kwargs}')

        attr = kwargs.pop('attr') if 'attr' in kwargs else ''
        
        if tag_name not in self.filter_instance_obj_dict:
            return
        
        if attr == '':
            #属性名が未指定の場合、タグ名のみでフィルターを検索、取得する。
            filter_obj = self.filter_instance_obj_dict.get(tag_name)
            return filter_obj
        
        filter_obj = self.filter_instance_obj_dict.get(tag_name)

        if attr in filter_obj:
            #タグ名で取得した内属性名でさらに対象を絞って検索、取得する。
            return filter_obj.get(attr)


    #当メソッド幾つか問題あり。しばらく凍結。
    def get_attrs_filter(self, name, get_method=None, **kwargs):
        ''' フィルターを取得する。フィルターオブジェクトによってメソッドで取得する場合はget_methodを使う。'''

        filter_instance = self.filter_instance_obj_dict.get(name, None)
        if filter_instance and hasattr(filter_instance, get_method):
            method = getattr(filter_instance, get_method)
            return method(**kwargs)


    @classmethod
    def create_filter(cls, tag_name, select_class, filterset_cls=None, filter_parameters:Dict=None, **kwargs):
        ''' フィルターを取得する。'''
        instance = cls(select_class, filterset_cls, filter_parameters, **kwargs)
        instance.create_attrs_filters(tag_name, **kwargs)
        element_filter = instance.get_filter_instance(tag_name)
        return element_filter


