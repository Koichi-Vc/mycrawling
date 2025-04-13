import importlib
import os
from pathlib import Path
from re import sub, escape
import logging
from sys import exc_info
from traceback import print_exc
from mycrawling.logs.debug_log import debug_logger

debug_logger.debug(f'package_: {__package__}')
debug_logger.debug(f'name: {__name__}')


def create_module_import_path(file_path):
    ''' モジュールファイルディレクトリパスをインポートパスに変換 '''
    back_slash = escape('\\')#\\をエスケープ。
    rep = f"[/ | {back_slash}]"
    path = Path(file_path)
    path_dir = str(path.parent) 
    module = path.stem
    print('create_module_import_path>>>>\n')
    print(f'rep : {rep} | path_dir: {path_dir}')
    print(f'file_path: {file_path}')
    import_path = sub(rep, '.', path_dir)
    print(f'import_path: {import_path}')
    print('create_module_import_path>>>>')

    joined_import_path = import_path + '.' + module if import_path != '.' else import_path+module

    return joined_import_path


def split_module_path(module_path, split_place=None):
    ''' moduleインポートパスをfrom節とimport節に該当する様に分割する。'''
    module_name = None
    obj_name = None
    if not module_path or not isinstance(module_path, str):
        logging.warning(f'モジュールパスが無効か又は文字列ではありません。module_path: {module_name}. type: {type(module_name)}')
        return module_name, obj_name
    
    if split_place is None:
        split_place = module_path.count('.')-1#最後のドット節がimport節に来る様に調整。25/1/06/

    replace_path = module_path.replace('.', '-', split_place).split('.', 1)
    split_path = [ph.replace('-', '.') for ph in replace_path]

    if isinstance(split_path, str):
        split_path = [split_path]

    if len(split_path) >= 2:
        module_name, obj_name = split_path
    else:
        module_name = split_path[0]

    return module_name, obj_name


def get_module_attr(module, attr_path):
    ''' モジュールのオブジェクトをパスをたどって順番に取得していく '''

    attr_names = attr_path.split('.')
    obj = None
    try:
        for attr in attr_names:
            #print(f'attr: {attr} | obj: {obj}')
            if not obj:
                obj = getattr(module, attr)

            elif obj:
                obj = getattr(obj, attr)
    except AttributeError as a:
        logging.error(f'モジュールメンバーのインポート失敗。memberpath: {attr_path}')
        print_exc()
    return obj


def get_module(module_path_name, split_place=None):
    ''' moduleを動的にインポートする。'''
    obj = None
    module = None
    split_place = module_path_name.count('.')#モジュールパスドットの数を数える

    #モジュールパスをfromとimport部分に分割するが、始めは分割せず、module_nameのみでimportを試みる。
    module_name, obj_name = split_module_path(module_path_name, split_place)
    
    if module_name:

        for place in reversed(range(split_place)):

            try:
                if place == 0:
                    #placeが0になった場合、module_nameをトップレベルパスにしてブレークする。
                    module_name, obj_name = split_module_path(module_path_name, split_place=place)
                    break
                module = importlib.import_module(module_name)#インポートに成功した時点でbreakする。
                break

            except ModuleNotFoundError:
                #モジュールを取得できなかった場合は、インポート出来る迄分割するドットを左へずらして行く。
                exc_type, exc_value, exc_traceback = exc_info()
                if module_path_name not in str(exc_value) and module_name not in str(exc_value):
                    #errorメッセージにインポートするモジュールやオブジェクト名が含まれていなかった場合、予期しないエラーが発生したと解釈し発出する。
                    module = None
                    break
                module = None
                module_name, obj_name = split_module_path(module_path_name, split_place=place)

        
        #break又はfor終了時点でのmoduleインポート状況を評価
        if module is None:
            #Noneの場合、改めてmodule_nameでインポートを試みて尚インポート不可能な場合は、ModuleNotFoundErrorが正式に発出される。
            module = importlib.import_module(module_name)
    
    if module and obj_name:
        obj = get_module_attr(module, obj_name)
      
    if obj:
        return obj
    else:
        return module 




