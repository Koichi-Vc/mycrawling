import json


def json_load(json_file, load_method=None):
    ''' jsonファイルの読み込み'''
    if load_method is None or callable(load_method):
        load_method = json.load
    return load_method(json_file)


def ref_files_load(file, load_method=None , **kwargs):
    ''' ファイルの読み込み'''
    with open(file, 'r', **kwargs) as f:

        if not load_method:
            data = f.read()
            
        elif callable(load_method):
            data = load_method(f)
    
    return data



class FilesLoader():

    default_load_file = ''
    
    @classmethod
    def file_load(cls, file=None, option='r', load_method=None, **kwargs):
        
        if file is None:
            file = cls.default_load_file

        with open(file, option, **kwargs) as f:

            if not load_method:
                data = f.read()
            elif callable(load_method):
                data = load_method(f)
        return data

    


