from abc import ABC
from mycrawling.utils.mediator import DataMediator
from mycrawling.logs.debug_log import debug_logger
#Var37.06.14.15a(24/07/25/時点のバージョン)

class BaseDataClass(ABC):

    __instance = None

    def __new__(cls, *args, **kwargs):
        debug_logger.debug(f'__instance: {cls.__instance}')
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        
        return cls.__instance

    #__init__はいらないかもしれない
    def __init__(self):
        self.datamediator = DataMediator()

    
    def sets_datamediator(self, instance):
        ''' mediator(仲介クラスインスタンス)をセットする '''
        self.datamediator = instance

    def data_notify_to_obj(self, instance=None, instance_name=None, **kwargs):
        ''' データクラスインスタンスが保持したデータの送り先 '''
        self.datamediator.register_notification_to(instance, instance_name, **kwargs)

    def get_field(self, field_name):
        if hasattr(self, field_name):
            return self.field_name
    
    def get_fields(self, *field_names):

        result_dict = dict()
        for name in field_names:
            value = self.get_field(name)
            if value:
                result_dict[name] = value
        return result_dict
    

    @classmethod
    def instance_factory(cls, *args, **kwargs):

        return cls(*args, **kwargs)
    


