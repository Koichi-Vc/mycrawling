from .loader import FilesLoader
from mycrawling.logs.debug_log import debug_logger

class ClassParameterLoader(FilesLoader):
    
    default_load_file = 'mycrawling/parameter_files/create_instance_parameters.json'
    
    def __init__(self, user_parameter_file_path=None, option='r', encoding='UTF-8', load_method=None, **kwargs):
        self.user_parameter_file_path = user_parameter_file_path
        self.option = option
        self.encoding = encoding
        self.load_method = load_method
        self.kwargs = kwargs
    
    def load_createinstance_parameter(self):
        ''' ファイルの読み込みを実行。'''
        file_path = None
        if not self.user_parameter_file_path:
            file_path = self.default_load_file
        else:
            file_path = self.user_parameter_file_path

        loaded_obj = self.file_load(file_path, self.option, self.load_method, encoding=self.encoding, **self.kwargs)
        debug_logger.debug(f'loaded_obj: {loaded_obj} | type: {type(loaded_obj)}')
        
        return loaded_obj

