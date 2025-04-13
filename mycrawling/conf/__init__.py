from .create_settings import CreateSetting
from mycrawling.utils.paths import join_current_dir
from mycrawling.utils.imports_module import create_module_import_path
from mycrawling.logs.debug_log import debug_logger


user_setting_import_path = None

create = CreateSetting(is_create_file=False)

def find_user_setting_module():
    ''' user_settingモジュールの所在を評価する。'''
    global user_setting_import_path

    user_setting_module_path = join_current_dir(create.dir_path)#ユーザー設定ファイルのフルパス生成
    debug_logger.debug(f'user_setting_module_path: {user_setting_module_path} | \n {user_setting_module_path.is_dir()}')
    
    parent_path = getattr(user_setting_module_path, 'parent', None)#ディレクトリ部分を取得
    is_directory = getattr(parent_path, 'is_dir')() if hasattr(parent_path, 'is_dir') else False#ディレクトリの所在を評価

    is_module_files = getattr(user_setting_module_path, 'is_file')() if hasattr(user_setting_module_path, 'is_file') else False#ユーザー用セッティングファイルの所在を評価
    debug_logger.debug(f'parent_path: {parent_path} | {is_directory} | {is_module_files}')

    if parent_path and is_directory and is_module_files:
        #ユーザー設定ファイルが存在した場合はインポートパスを生成する。
        module_import_path = create_module_import_path(create.dir_path)
        debug_logger.debug(f'module_import_path: {module_import_path}')

        user_setting_import_path = module_import_path

        return user_setting_import_path
    else:
        return None
    

user_setting_import_path = find_user_setting_module()


