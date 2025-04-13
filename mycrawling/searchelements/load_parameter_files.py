from pathlib import Path
from mycrawling.utils.loaders.loader import json_load, ref_files_load, FilesLoader
from mycrawling.logs.debug_log import debug_logger
''' 要素検索のフィルターを作成する為の引数をまとめたjsonファイルを読み込む。 '''


default_load_file = 'mycrawlingpack/parameter_files/elements_filter_arguments.json'

user_parameters_file_path = Path('user_reftexts_dir/elements_filter_arguments.json')#ユーザーが用意する要素検索フィルター用のパラメータファイル

elements_filter_parameters = dict()

#get_filters_parametersの新コード
def get_filter_parameters():
    ''' フィルターに用いるパラメータ値をまとめたjsonファイルを読み込む '''
    global elements_filter_parameters
    #parameterhandler_cls = None#parameterhandlerクラス
    #is_required_param = None#parameterhandlerが引数を必須とするかチェック
    load_file = user_parameters_file_path if user_parameters_file_path.is_dir() else default_load_file
    elements_filter_parameters = ref_files_load(load_file, json_load, encoding='UTF-8')

    debug_logger.debug(f'elements_filter_parameters: {elements_filter_parameters}')
    if 'None' in elements_filter_parameters.keys():
        #キー名'None'をNoneに変換。特にタグを指定していないフィルターを表す。
        elements_filter_parameters[None] = elements_filter_parameters['None']
    return elements_filter_parameters


class FilterParameterLoader(FilesLoader):
    '''
    args:
        user_parameter_file_path: ユーザーが用意したパラメータファイルのパスを保持する。
        option:
        default_user_parameter_file_path: デフォルトで
    '''

    default_load_method = None#デフォルトで使用するファイル読み込み用メソッド。
    default_load_file = Path('mycrawling/parameter_files/elements_filter_arguments.json')
    
    def __init__(self, user_parameter_file_path=None, option='r', encoding='UTF-8', load_method=None, **kwargs):
        self.user_parameter_file_path = Path(user_parameter_file_path)
        self.option = option
        self.encoding = encoding
        self.load_method = load_method if callable(load_method) else self.default_load_method
        self.elements_filter_parameters = None
    
    def load_filter(self, **kwargs):

        load_file = self.user_parameter_file_path if self.user_parameter_file_path.is_dir() else self.default_file_path
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


if __name__ == '__main__':
    get_filter_parameters()
    debug_logger.debug(f'if __name__ == __main__>>>')
    debug_logger.debug(F'elements_filter_parameters: {elements_filter_parameters}')

    