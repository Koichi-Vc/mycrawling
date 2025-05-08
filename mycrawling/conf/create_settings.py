from pathlib import Path
import shutil
from mycrawling.utils.paths import join_current_dir
from mycrawling.utils.imports_module import create_module_import_path
#from mycrawling.logs.debug_log import debug_logger


''' ユーザー設定ファイルをデフォルトの設定ファイルをコピーして生成する。 '''
print(f'__file__: {__file__}')
base_dir = Path(__file__).parent.parent.parent
default_setting_file = base_dir.joinpath(Path('mycrawling/conf/setting.py'))#パッケージのデフォルトセッティングパス
print(f'default_setting_file: {default_setting_file}')
created_user_setting_import_path = None


class CreateSetting:
    
    setting_module_name = 'user_settings'
    user_setting_module_directory = Path('mycrawling_user/')

    def __init__(self, directory=None, is_create_file=True):
        self.user_setting_import_path = None

        self.module_file = self.setting_module_name + '.py'
        if directory is None:
            self.directory = self.user_setting_module_directory 
        else:
            self.directory = Path(directory)
        self.dir_path = self.directory.joinpath(self.module_file)
        
        if is_create_file is True:
            self.create_settings_file()


    #create_settings_fileの修正
    def create_settings_file(self):
        global created_user_setting_import_path

        #user_setting_module_dir_path = current_path.joinpath(self.dir_path)
        user_setting_module_dir_path = join_current_dir(self.dir_path)#dir_pathの
        print(f'user_setting_module_dir_path: {user_setting_module_dir_path}')
        print(f'user_setting_module_dir_path.parent: {user_setting_module_dir_path.parent}')
        print(f'user_setting_module_dir_path.name: {user_setting_module_dir_path.name}')
        print(f'user_setting_module_dir_path.is_dir: {user_setting_module_dir_path.parent.is_dir()}')
        
        if not user_setting_module_dir_path.parent.is_dir():
            user_setting_module_dir_path.parent.mkdir(parents=True)#ディレクトリ生成
            #user_setting_module_dir_path.touch()#ファイル生成
            shutil.copy(default_setting_file, user_setting_module_dir_path)#コピー
            #ユーザー用設定ファイル生成時にベースディレクトリをsetting.pyの__file__にしておく。
            package_base_dir = __file__
            with open(user_setting_module_dir_path, mode='+r', encoding='UTF-8') as f:
                content = f.read()
                replaced_file_path = content.replace('__file__', f'"{package_base_dir}"')
                f.seek(0)
                f.write(replaced_file_path)
            created_user_setting_import_path = create_module_import_path(self.dir_path)
            print(f'created_user_setting_import_path: {created_user_setting_import_path}')


if __name__ == '__main__':
    create_dir = CreateSetting()


