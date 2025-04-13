import logging
from selenium.webdriver.support.ui import WebDriverWait
from mycrawling.utils.imports_module import get_module
from mycrawling.logs.debug_log import debug_logger


class BasebWebDriverContextManager():
    ''' webdriverのセッティング、起動、終了を管理するベースクラス'''
    '''
    メソッド:
        setting_service:
            Serviceクラスをインスタンス化するためのメソッド。
    '''
    webdriver_object = None
    service_class = None
    options = None

    def __init__(self, driver_filename, timeout, service_instance=None, **kwargs):
        if not self.webdriver_object:
            logging.warning('webdriverが定義されていません。webdriver_objectにドライバを割り当ててください。')

        self.driver_filename = driver_filename#webdriverのディレクトリパスを指定
        self.timeout = timeout
        self.kwargs = kwargs
        if isinstance(service_instance, str) and ('/' not in service_instance and '\\' not in service_instance):
            #serviceインスタンスがインポートパスの場合はインポートを試みる。
            service_instance = get_module(service_instance)

        elif not service_instance and self.service_class and self.driver_filename:
            #serviceインスタンスが無く、Serviceクラスとwebdriverパスがある場合はserviceインスタンスを生成する。
            service_instance = self.setting_service(self.driver_filename)
        
        self.service_instance = service_instance
        debug_logger.debug(f'self.service_instance: {self.service_instance}')

    def __enter__(self):
        if self.service_instance:
            self.driver = self.webdriver_object(service=self.service_instance, options=self.options, **self.kwargs)
        else:
            self.driver = self.webdriver_object(options=self.options, **self.kwargs)
        self.wait = WebDriverWait(self.driver, self.timeout)
        return self  

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.driver.quit()


    def driver_get(self, *args, **kwargs):
        self.driver.get(*args, **kwargs)

    @classmethod
    def setting_service(cls, *args,**kwargs):

        if callable(cls.service_class):
            service_instance = cls.service_class(*args, **kwargs)
        else:
            raise TypeError('Serviceクラスが無効か、設定されていません。service_classに設定してください。')
        return service_instance


    def show_service_instance(self):
        ''' Serviceインスタンスを返す'''
        return self.service_instance


    def add_option(self, *values):
        pass


