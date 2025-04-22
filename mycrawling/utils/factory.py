from abc import ABC, abstractmethod
from mycrawling.conf.data_setting import ref_dataconfig, Ref_DataConfig
from .imports_module import get_module
from .method_parse import run_method, has_param_names
from mycrawling.utils.loaders.loader import FilesLoader, json_load
from mycrawling.logs.debug_log import debug_logger


debug_logger.debug(f'ref_dataconfig: {ref_dataconfig}')

class AbstractFactory(ABC):

    @abstractmethod
    def create_instance(self, class_name, arguments):
        pass

    @abstractmethod 
    def create_instances(self, **parameters):
        pass


class Factory(AbstractFactory):
    ''' 実行する前に、data_setting.Ref_DataConfigのインスタンス化をする。'''
    #使用するクラスのインポートパスを取得、
    if not ref_dataconfig or not getattr(ref_dataconfig, 'setting_conf', None):
        ref_dataconfig = Ref_DataConfig.ref_dataconfig_factory()#設定ファイルの初期化が未実行だった場合は初期化を実行する。
    debug_logger.debug(f'ref_dataconfig: {ref_dataconfig}')

    USE_CLASSES = ref_dataconfig.get_conf_value('USE_CLASSES')
    LAZY_INSTANCES_CLASS = ref_dataconfig.get_conf_value('LAZY_INSTANCES_CLASS')

    def __init__(self, classes:dict=None, conf_class_name=None, **kwargs):
        '''
        conf_class_name:
            settingオブジェクトに登録されているクラスを指定する。
        classes:
            クラス名とインポートパスの辞書型を受けとる。何も指定しない場合、USE_CLASSESが代入される。
        '''
        self.classes = dict()
        self.class_objects = dict()#インポートしたクラスを保持。
        
        self.class_instances = dict()#インスタンス
        self.lazy_instances_class = kwargs.pop('lazy_instances_class', dict())#インスタンス化を遅延するクラスを保持。
        conf_lazy_instances_class = kwargs.pop('conf_lazy_instances_class', None)
        self.lazy_instances_class_objects = dict()
        self.no_datamediator_classes = []
        
        if conf_class_name in self.USE_CLASSES:
            classes.update({conf_class_name: self.USE_CLASSES.get(conf_class_name)})
        if not conf_lazy_instances_class and self.LAZY_INSTANCES_CLASS:
            self.lazy_instances_class.update(self.LAZY_INSTANCES_CLASS)

        if not classes:
            classes = self.USE_CLASSES
        self.classes.update(classes)#インポート, インスタンス化を行うクラスをクラス名-インポートパスの辞書型で保持。

        #if not ref_dataconfig or not getattr(ref_dataconfig, 'setting_conf', None):
        #    ref_dataconfig = self.ref_dataconfig
        debug_logger.debug(f'ref_dataconfig: {ref_dataconfig}')
        self.datamediator = get_module(ref_dataconfig.get_conf_value('USE_MEDIATOR_PATH'))


    def import_classes(self, class_name=None, retainer=None, **class_paths):
        ''' クラスをインポートする。'''
        if retainer is None:
            retainer = self.class_objects
        if class_name and class_name in self.classes.keys():
            return {class_name: get_module(self.classes.get(class_name))}
        
        elif class_name and class_name in class_paths.keys():
            return {class_name: get_module(class_paths.get(class_name))}
        
        imported_class = dict()
        if not class_paths:
            class_paths = self.classes
        
        for class_name, value in class_paths.items():

            if isinstance(value, str):
                value = get_module(value)
            if value:
                imported_class[class_name] = value
        retainer.update(imported_class)
        return imported_class        


    def import_lazy_instances_class(self, class_name=None):
        imported_class = self.import_classes(class_name, retainer=self.lazy_instances_class_objects, **self.lazy_instances_class)
        #self.lazy_instances_class.update(imported_class)
        return imported_class


    def get_class(self, class_name):
        ''' クラスを取得する。'''
        if class_name in self.class_objects.keys():
            return self.class_objects.get(class_name)
        
        elif class_name in self.classes.keys():
            #インポート済みクラスにない場合は、保持しているクラス辞書からインポートを行う。
            class_path = self.classes.get(class_name)
            class_object = self.import_classes(class_name=class_path)
            self.class_objects.update(**class_object)
            return class_object.get(class_name)


    def create_instance(self, class_name, arguments=tuple(), **kwargs):
        ''' クラスのインスタンス化を行う。'''
        instance = None
        datamediator = kwargs.get('datamediator', None)
        class_obj = self.get_class(class_name)

        if not class_obj:
            raise KeyError(f'{class_name}が存在しないか又はインポートに失敗しました。')
        
        if 'datamediator' not in arguments and datamediator is None and has_param_names(class_obj, 'datamediator'):
            #クラスのコンストラクタ引数にdatamediatorが存在し、datamediatorがargumentsに含まれていない場合は追加する。
            arguments['datamediator'] = self.datamediator
        debug_logger.debug(f'class_obj: {class_obj}  | arguments: {arguments}')
        if class_obj:
            instance = run_method(arguments, class_obj)
            self.class_instances[class_name] = instance

        return instance
    

    def create_instances(self, **parameters):
        #USE_CLASSESに登録されたクラスをインスタンス化していく
        instance_dict = dict()
        param_keys = parameters.keys()
        class_names = self.class_objects.keys()
        for class_name in class_names:

            if class_name in param_keys:
                instance = self.create_instance(class_name, parameters.get(class_name))
            else:
                instance = self.create_instance(class_name)
            instance_dict[class_name] = instance
        return instance_dict


    #data_settingモジュールから移動。
    def create_data_cls_instance(self, arguments=None, select_cls=None, add_mediator=False, override=True):
        ''' パラメータを元にデータクラスインスタンスを生成する。 '''
        '''
        add_mediator:
            Trueの場合、datamediatorへオブジェクトを登録する。
        override:
            Trueを指定した場合、同じ名前で登録されているオブジェクトは上書きされる。
        '''

        #datacls_objects = setting.registry_data_class_instance

        datacls_objects = self.ref_dataconfig.get_conf_value('REGISTRY_DATA_CLASS_INSTANCE')
        ref_texts_arguments_path = arguments if arguments else ref_dataconfig.get_conf_value('REFERENCE_TEXTS_FILES')
        ref_texts_arguments = self.get_param_json_file(ref_texts_arguments_path)
        data_cls_instances = dict()
        class_names = list()
        if select_cls:
            class_names = select_cls
        else:
            class_names = datacls_objects
        
        for cls_name in class_names:
            parameter = ref_texts_arguments.get(cls_name, None)#パラメータの取得
            module_path = datacls_objects[cls_name]#データクラスモジュールパスを取得
            module = get_module(module_path)#モジュールの取得

            if parameter and module:
                instance = module(**parameter)
                data_cls_instances[cls_name] = instance
            
                #register_to_datamediatorに担わせるかどうか検討中。
        if add_mediator is True:
            self.register_to_datamediator(override=override, **data_cls_instances)
        
        return data_cls_instances


    #data_settingモジュールから移動。
    def register_to_datamediator(self, override=True, **values_dict):
        ''' datamediatorへオブジェクトを登録する。'''
        self.datamediator.register_object(values_dict, override)


    def get_param_json_file(self, file):
        ''' データクラスインスタンス用パラメータをまとめたjsonファイルを読み込む '''
        #parameters = ref_files_load(file, json_load, encoding='UTF-8')
        parameters = FilesLoader.file_load(file, load_method=json_load, encoding='UTF-8')
        return parameters

