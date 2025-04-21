from re import match as re_match
from .create_settings import created_user_setting_import_path
from . import setting
from . import user_setting_import_path
from mycrawling.utils.imports_module import get_module
from mycrawling.utils.loaders.loader import json_load, FilesLoader
from mycrawling.utils.mediator import DataMediator
from mycrawling.logs.debug_log import get_debug_log

#ここでdebug_logをインポートしてデバッグログを共有するやり方をしてみる。

datamediator = DataMediator()

#setting_conf = dict()#get_conf_valueを用意した為うまく行けば不要になる。

class Ref_DataConfig():
    '''
    設定ファイルの内容を纏める。纏めた設定内容は、setting_confに辞書で保持され、get_conf_valueでアクセス可能になる。
    また、各種データクラスのインスタンス化もここで可能。その際は、create_data_cls_instanceを実行する。尚datamediatorインスタンス
    への登録はデフォルトでFalseになっている為登録する場合はadd_mediatorをTrueにする。

    '''
    '''
    初期化時にjsonファイルからパラメータの取得を行う。
    args:
        parametor_jsonfile:
            default:None
            パラメータをまとめたjsonファイルを受け取る。何も渡さない場合、default_ref_text_fileを読み込む。
        parametor_dict:
            ファイルでは無く辞書型で渡す場合、此のパラメータへ渡す。
    '''
    #default_ref_text_file = 'mycrawling/parameter_files/ref_textfiles/ref_texts.json'
    default_ref_text_file = setting.REFERENCE_TEXTS_FILES
    
    '''先にRetainSettingConfをインスタンス化したreteinsettingconfにしてそれを
    どうにかしてここにいれるやり方にしてみる。
    '''

    def __init__(self, parametor_jsonfile=None, parametor_dict=None, retainsettingconf=None, **kwargs):

        reading_setting = kwargs.pop('reading_setting', True)
        self.parametor_jsonfile = parametor_jsonfile
        self.parametor_dict = parametor_dict
        self.parameters = None
        self.ref_texts_arguments = None
        self.registry_class_objcts = dict()#REGISTRY_CLASSからインポートしたクラスを保持。
        
        self.datamediator = datamediator
        self.retainsettingconf = retainsettingconf if retainsettingconf is not None else RetainSettingConf()
        self.retainsettingconf.setting_file = user_setting_import_path if user_setting_import_path else created_user_setting_import_path
        if reading_setting is True:
            self.setting_conf = self.retainsettingconf.read_settings()
        else:
            self.setting_conf = dict()
        self.default_ref_text_file = self.setting_conf.get('REFERENCE_TEXTS_FILES')
        #setting_conf = self.setting_conf
        get_debug_log(debug=self.setting_conf.get('Debug'))#デバッグ用のログを設定する。

    def get_param_json_file(self, file):
        ''' データクラスインスタンス用パラメータをまとめたjsonファイルを読み込む '''

        parameters = FilesLoader.file_load(file, load_method=json_load, encoding='UTF-8')
        return parameters


    def get_conf_value(self, configparameter, select_attr=None, **kwargs):
        ''' setting_confから特定の設定情報を取得する。'''
        kwg_keys = kwargs.keys()

        if configparameter in self.setting_conf:
            config_value = self.setting_conf.get(configparameter, None)
        elif 'default' in kwg_keys:
            config_value = kwargs.get('default')
        else:
            raise KeyError(f'settingに定義されていないパラメータ値です。| {configparameter}')

        if config_value and select_attr:
            ''' 取得した設定変数から更に属性を参照する。'''

            if select_attr in config_value:
                value = config_value.get(select_attr)
            elif hasattr(config_value, select_attr):
                value = getattr(config_value, select_attr)
            elif 'default' in kwg_keys:
                return kwargs.get('default')
            else:
                raise AttributeError(f'取得したパラメータに指定した属性は見つかりませんでした。| 設定情報:{config_value} | 属性: {select_attr}')
            return value
        else:
            return config_value
    
    def has_config(self, configparameter):
        result = False
        if configparameter in self.setting_conf:
            result = True
        return result

    
    @classmethod
    def ref_dataconfig_factory(cls, parametor_jsonfile=None, parametor_dict=None, retainsettingconf=None):
        ''' RefDataConfigクラスをインスタンス化しグローバル変数に保持する。'''
        global ref_dataconfig
        ref_dataconfig = cls(parametor_jsonfile, parametor_dict, retainsettingconf)
        return ref_dataconfig



class RetainSettingConf:
    ''' setting情報を保持する。'''

    def __init__(self, settings_file=None):
        self.setting_module = None
        self.setting_file = settings_file
        #self.setting_tuple = (
        #    'REGISTRY_CLASS',
        #    'REGISTRY_DATA_CLASS_INSTANCE',
        #    'ANCHOR_SEARCH_MODULE'
        #)

        self.setting_tuple = (
            val for val in dir(setting) if (val.isupper() or val.istitle()) and not bool(re_match(r'[__]', val))
        )
        self.setting_conf = dict()


    @property
    def setting_file(self):
        return self._setting_file

    
    @setting_file.setter
    def setting_file(self, import_path):

        if not hasattr(self, 'setting_file'):
            self._setting_file = None

        if import_path:
            #path = Path(file_path)
            self.setting_module = get_module(import_path)
            self._setting_file = import_path
        

    def read_settings(self):
        ''' セッティングファイルを読み込む。 '''
        for setting_item in self.setting_tuple:

            if self.setting_module and hasattr(self.setting_module, setting_item):

                self.setting_conf[setting_item] = getattr(self.setting_module, setting_item)
            else:
                self.setting_conf[setting_item] = getattr(setting, setting_item)

        return self.setting_conf
    

    def get_setting_value(self, item_name):
        ''' 設定内容を参照する。 '''
        return self.setting_conf.get(item_name, None)

#デフォルトでは設定の読み込みはFalse
ref_dataconfig = Ref_DataConfig(reading_setting=False, default=None)

