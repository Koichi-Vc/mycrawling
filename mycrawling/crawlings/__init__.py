from mycrawling.conf.data_setting import ref_dataconfig
from mycrawling.utils.imports_module import get_module
from mycrawling.utils.loaders.parameters import ClassParameterLoader

#25/03/21/; 不完全なメソッド。廃止の可能性。
def load_use_classes(class_name, parameter=None, parameter_path=None, **kwargs):
    ''' 設定ファイルから使用クラス情報を取得し、インポートとインスタンス化を行う。'''
    USE_CLASSES = ref_dataconfig.get_conf_value(kwargs.pop('use_classes', 'USE_CLASSES'))


    class_path = ref_dataconfig.get_conf_value(USE_CLASSES, class_name)
    arguments = None
    if isinstance(parameter, str):
        arguments = ref_dataconfig.get_conf_value(parameter)
    elif parameter_path:
        loader = ClassParameterLoader(parameter_path)
        arguments = loader.load_createinstance_parameter()

    class_obj = get_module(class_path)

    if arguments:
        return class_obj(**arguments)
    else:
        return class_obj()


