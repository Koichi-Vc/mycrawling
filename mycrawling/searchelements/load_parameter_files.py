from pathlib import Path
from mycrawling.utils.loaders.loader import json_load, ref_files_load, FilesLoader
#from mycrawling.logs.debug_log import debug_logger
from mycrawling.conf.data_setting import ref_dataconfig
''' 要素検索のフィルターを作成する為の引数をまとめたjsonファイルを読み込む。 '''

'''パスがすべて実質相対パスになってしまっている問題を解決する。 25/04/23'''


class FilterParameterLoader(FilesLoader):
    '''
    args:
        user_parameter_file_path: ユーザーが用意したパラメータファイルのパスを保持する。
        option:
        default_user_parameter_file_path: デフォルトで
    '''

    default_load_method = None#デフォルトで使用するファイル読み込み用メソッド。
    default_load_file = Path(ref_dataconfig.get_conf_value('FILTER_PARAMETER_FILE', default=''))
    
    def __init__(self, user_parameter_file_path=None, option='r', encoding='UTF-8', load_method=None, **kwargs):
        self.user_parameter_file_path = Path.cwd().joinpath(Path(user_parameter_file_path))
        self.option = option
        self.encoding = encoding
        self.load_method = load_method if callable(load_method) else self.default_load_method
        self.elements_filter_parameters = None
    
    def load_filter(self, **kwargs):
        print(f'FilterParameterLoader.load_filter>>>>>')
        print(f'self: {self} | kwargs: {kwargs}')
        load_file = self.user_parameter_file_path if self.user_parameter_file_path.is_dir() else self.default_load_file
        elements_filter_parameters = self.file_load(
            load_file,
            option=self.option,
            load_method=self.load_method,
            encoding=self.encoding,
            **kwargs)

        if 'None' in elements_filter_parameters.keys():
            elements_filter_parameters[None] = elements_filter_parameters.pop('None')
        self.elements_filter_parameters = elements_filter_parameters

        return self.elements_filter_parameters


    