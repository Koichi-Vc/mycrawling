import json
from mycrawling.conf.data_setting import Ref_DataConfig, ref_dataconfig
from mycrawling.utils.factory import Factory
from mycrawling.utils.imports_module import get_module
from mycrawling.utils.loaders.loader import FilesLoader
from mycrawling.utils.loaders.parameters import ClassParameterLoader
from mycrawling.logs.debug_log import debug_logger


class Main():
    ''' ページのクローリングをスタートする。'''
    WEBDRIVER_SERVICE_PARAM = None if not ref_dataconfig else ref_dataconfig.get_conf_value('WEBDRIVER_SERVICE_PARAM', default=dict())
    WEBDRIVER_MANAGER_PARAM = None if not ref_dataconfig else ref_dataconfig.get_conf_value('WEBDRIVER_MANAGER_PARAM', default=dict())

    def __init__(self, webdriver_manager=None, crawling_obj=None, factory_instance=None, loader=None, *args, **kwargs):

        if getattr(ref_dataconfig, 'setting_conf', None):
            ref_dataconfig = Ref_DataConfig.ref_dataconfig_factory()
            self.WEBDRIVER_SERVICE_PARAM = ref_dataconfig.get_conf_value('WEBDRIVER_SERVICE_PARAM', default=dict())
            self.WEBDRIVER_MANAGER_PARAM = ref_dataconfig.get_conf_value('WEBDRIVER_MANAGER_PARAM', default=dict())

        debug_logger.debug(f'ref_dataconfig: {ref_dataconfig}')
        self.webdriver_manager = webdriver_manager if webdriver_manager else get_module(ref_dataconfig.get_conf_value('WEBDRIVER_MANAGER'))

        if crawling_obj is None:
            obj_path = ref_dataconfig.get_conf_value('CRAWLING_CLASS')
            crawling_obj = get_module(obj_path)
        debug_logger.debug(f'WEBDRIVER_SERVICE_PARAM: {self.WEBDRIVER_SERVICE_PARAM}')
        self.crawlig_obj = crawling_obj
        self.args = args
        self.kwargs = kwargs
        classes = kwargs.pop('classes', None)

        if factory_instance:
            self.factory = factory_instance
        else:
            self.factory = Factory(classes=classes)
            self.factory.import_classes()
            self.factory.import_lazy_instances_class()
            self.factory.create_data_cls_instance(add_mediator=True)#データクラスインスタンスの生成。
        debug_logger.debug(f'factory.class_objects: {self.factory.class_objects}')
        debug_logger.debug(f'factory.class_instances: {self.factory.class_instances}')
        if not loader:
            loader = ClassParameterLoader(load_method=json.load)
        parameters = None
        if isinstance(loader, ClassParameterLoader):
            parameters = loader.load_createinstance_parameter()
        elif issubclass(loader, FilesLoader):
            parameters = loader.file_load(**kwargs)

        self.parameters = parameters
        debug_logger.debug(f'parameters: {self.parameters}')
        if factory_instance:
            instance_dict = self.factory.class_instances
        else:
            instance_dict = self.factory.create_instances(**self.parameters)
        debug_logger.debug(f'instance_dict: {instance_dict}')
        self.factory.datamediator.register_object(instance_dict)#datamediatorに生成したインスタンスを登録する。
        self.factory.datamediator.register_object(self.factory.lazy_instances_class_objects)#インスタンス化を遅延するクラスを登録する。

    def start(self, input_url, *args, **kwargs):

        if hasattr(self.webdriver_manager, 'setting_service') and 'service_instance' not in self.WEBDRIVER_MANAGER_PARAM and self.WEBDRIVER_SERVICE_PARAM:
            service_instance = self.webdriver_manager.setting_service(**self.WEBDRIVER_SERVICE_PARAM)
            self.WEBDRIVER_MANAGER_PARAM.update(service_instance=service_instance)
            debug_logger.debug(f'self.service_instance: {service_instance}')
        debug_logger.debug(f'self.WEBDRIVER_MANAGER_PARAM: {self.WEBDRIVER_MANAGER_PARAM}')

        if not args:
            args = self.args
        if not kwargs:
            kwargs = self.kwargs
        
        with self.webdriver_manager(**self.WEBDRIVER_MANAGER_PARAM) as driver_manager:

            self.crawl =self.crawlig_obj(driver_manager, input_url, *args, **kwargs)
            self.factory.datamediator.register_object({'crawling_class':self.crawl})
            self.crawl.myscraping(*args, **kwargs)
        
        if hasattr(self.crawl, 'data_frame'):
            return self.crawl.data_frame
        else:
            return self.crawl
        


