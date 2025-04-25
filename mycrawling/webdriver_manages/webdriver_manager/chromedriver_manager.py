from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from .basemanager import BasebWebDriverContextManager
from mycrawling.utils.imports_module import get_module
import chromedriver_binary

''' chromiumバージョンのウェブドライバー起動モジュールを作成する。'''

remote_debugging_pipe = '--remote-debugging-pipe'

class ChromeWebDriverContextManager(BasebWebDriverContextManager):
    ''' Chromium専用のwebdriverマネージャ '''
    '''
    optionsについて:
        '--remote-debugging-pipe'はchromiumの場合追加されていないと起動時に予期しない挙動をする場合がある。
    '''

    default_options = [
        '--disable-dev-shm-usage',
        '--disable-software-rasterizer',
        '--remote-debugging-pipe'
    ]

    webdriver_object = Chrome
    service_class = Service
    options = Options()
    
    def __init__(self, driver_filename=None, timeout=20, service_instance=None, option_arguments=None,include_remote_debugging_pipe=True, **kwargs):

        self.driver = None
        self.error_logger = None
        self.error_message = list()
        op_arguments = option_arguments if option_arguments else self.default_options

        if not isinstance(op_arguments, list):
            raise TypeError('option_argumentsはList, Tuple, Set型のいずれかを受け取ります。')
        
        elif remote_debugging_pipe not in op_arguments and include_remote_debugging_pipe:
            #'--remote-debugging-pipe'がなかった場合且つ--remote-debugging-pipeの追加指示が有る場合、追加する。
            op_arguments.append(remote_debugging_pipe)
        self.add_option(*op_arguments)

        super().__init__(driver_filename, timeout, service_instance=service_instance, **kwargs)
    
    @classmethod
    def setting_service(cls, executable_path=None, *args, **kwargs):
        if isinstance(executable_path, str) and ('/' not in executable_path and '\\' not in executable_path):
            executable_path = get_module(executable_path)
        if executable_path:
            return super().setting_service(executable_path, *args, **kwargs)
        else:
            return super().setting_service(*args, **kwargs)


    def add_option(self, *values):
        ''' webdriverに指定するオプションを追加する。'''
        for value in values:
            if value not in self.options.arguments:
                self.options.add_argument(value)


