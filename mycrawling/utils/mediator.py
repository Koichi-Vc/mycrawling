from typing import Union, Dict
from abc import ABC, abstractmethod
from .imports_module import get_module
from mycrawling.logs.debug_log import debug_logger

#Var37.06.14.15a(24/07/25/時点のバージョン)
class BaseDataMediator(ABC):
    ''' DataMediatorクラスの抽象基底クラス '''
    ''' 仲介クラスを定義するにあたり、以下のメソッドを用いる。 '''

    @abstractmethod
    def get_attr(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_instance(self, *args, **kwargs):
        pass
    
    @abstractmethod
    def notify(self, *args, **kwargs):
        pass


#Var37.06.14.15a(24/07/25/時点のバージョン)
class DataMediator(BaseDataMediator):

    ''' 
    インスタンスが生成した値やオブジェクトを他のクラスインスタンスへ共有するクラス。
 
    共有するオブジェクトの生成者はDataMediatorインスタンスを保持する。
    共有先のオブジェクト(notification_to)は必ずdatamediator_updateメソッドを定義していなければならない。
    
    notifyメソッドが実行された際にnotification_toのdatamediator_updateメソッドを呼び出し、変更内容を反映する。
    datamediator_updateメソッドの実装例:
        def datamediator_update(self, value):
            self.item = value
    '''

    def __init__(self, only_instance_exact_match=False, **kwargs):
        '''
        args:
            registry_notify_objects:
                生成されたオブジェクトの共有先インスタンスを保持する。
            
            registry_notify_object_set:
                生成されたオブジェクトの共有先インスタンスを保持する。
                登録時にキーが指定されなかった場合、ここに登録される。

            only_instance_exact_match:
                共有先オブジェクト検索フィルタをインスタンス名での完全一致に絞る場合はTrueを指定。
            
            custom_filter:
                登録オブジェクト検索にカスタムのフィルターを使う場合はこの引数が受け取る。
        '''
        self.registry_notify_objects = dict()#送受信者の登録
        self.registry_notify_object_set = set()#送受信者の登録※登録時にキーを指定しない場合に格納される場所。
        self.default_instance_name = None
        self.filter_exact_match = lambda notify, object_name: notify == object_name
        
        self.filter_isinstance_or_exact_match = lambda notify, object_name : isinstance(notify, object_name) or notify == object_name 
        
        custom_filter = kwargs.pop('custom_filter', None )
        self.custom_filter = custom_filter if custom_filter and callable(custom_filter) else custom_filter
        
        debug_logger.debug(f'only_instance_exact_match: {only_instance_exact_match}')

        if custom_filter:
            self.search_notify_to_filter = self.custom_filter

        elif only_instance_exact_match:
            self.search_notify_to_filter = self.filter_exact_match

        else:
            self.search_notify_to_filter = self.filter_isinstance_or_exact_match

       
    #register_notification_toの後継メソッド
    def register_object(self, objects_dict:Dict, override=True):
        '''
        datamediatorインスタンスへオブジェクトをkey-valueで登録する。
        override:
            Trueの場合、既に存在している値は上書きされる。Falseの場合、既に存在している値が優先される。
        '''
        if not isinstance(objects_dict, dict):
            raise TypeError('obj_dictはdict型を取ります。')

        for key, obj_value in objects_dict.items():

            if isinstance(obj_value, str):
                obj_value = get_module(obj_value)
                
            if override is True:
                self.registry_notify_objects[key] = obj_value
            else:
                self.registry_notify_objects.setdefault(key, obj_value)


    #find_notification_filterからの名称変更25/01/15/
    def find_all_notification(self, object_name):
        ''' 辞書値を元に登録しているクラスとインスタンスをフィルター検索。戻り値はリスト '''
        '''
        arg:
            object_name:
                検索対象の登録オブジェくトを受け取り、該当するインスタンス、クラスオブジェクトをフィルターする。
        datamediatorは値としてインスタンスやクラスオブジェクトを持つ事が想定されている為、
        '''
        searched_obj = []

        if isinstance(object_name, str):
            searched_obj = [
                self.registry_notify_objects[notify] for notify in self.registry_notify_objects.keys() if self.filter_exact_match(notify, object_name)
                ]
            
        else:#self.search_notify_to_filterはオブジェクトがキーになっていることを想定したフィルター
            #現在実用性に疑問が出始めたことと可読性の観点から廃止するかもしれない。
            searched_obj = [
                notify for notify in self.registry_notify_objects.values() if self.search_notify_to_filter(notify, object_name)
                ]
        return searched_obj


    #find_notification_dictからの名称変更25/01/15/
    def find_notification(self, object_name):
        ''' 辞書値を元に登録しているクラスとインスタンスを検索し、該当した最初の値を返す。 '''
        ''' クラスとインスタンスを辞書値で検索し該当した最初のオブジェクトを返す。'''
        searched_result = []

        searched_obj = [
            notify for notify in self.registry_notify_objects.values() if self.search_notify_to_filter(notify, object_name)
            ]

        debug_logger.debug(f'object_name: {object_name} | search_notify_to_filter: {self.search_notify_to_filter.__name__} | searched_obj: {searched_obj}')
        
        if searched_obj:
            searched_result = searched_obj[0]
        return searched_result      

    
    #search_notify_objectへ名称変更する予定
    def search_notify_object(self, object_name:Union[str, type], **kwargs):
        ''' registry_notify_objectsへ登録済みのオブジェクトを名前検索する。 '''
        '''
        object_name:
            検索するインスタンスを受け取る。
            str: 登録済みから辞書キー検索をする。
            type: クラスオブジェクトの場合、該当するクラスインスタンス全てを検索する。
        '''
        debug_logger.debug(f'object_name: {object_name} | type: {type(object_name)}')

        objects = None
        if isinstance(object_name, str):
            objects = self.registry_notify_objects.get(object_name, None)
            
        elif isinstance(object_name, (type, object)):
            objects = self.find_notification(object_name)
        
        debug_logger.debug(f'objects: {objects}')

        if objects == []:
            objects = None
        
        return objects


    def get_attr(self, object_name, attr_value):
        '''object_nameを送信先の中(registry_notify_objects)から検索し、指定した属性を返す。'''
        '''
        object_name:
            検索する送信先
        attr_value:
            object_nameから取得する属性
        '''
        value = None
        instance = self.search_notify_object(object_name)#インスタンスの検索

        if instance:
            value = getattr(instance, attr_value, None)
            debug_logger.debug(f'instance: {value}')
        return value


    def get_instance(self, instance_name):
        ''' 登録済みのインスタンスを取得する。 '''

        instance = None
        instance = self.search_notify_object(instance_name)#インスタンスの検索
        if instance:
            return instance

    def has_registry_obj(self, name):
        ''' 登録済みのオブジェクトの中に対象の名前が含まれているか評価する。'''
        return name in self.registry_notify_objects.keys()
    


    def notify(self, attr_value, **kwargs):

        '''
        データの生成者が発信する場合に用いる。
        arg:
            attr_value: registry_notify_objectsへ共有するデータ。

        kwargs:

            notification_to: 通知の送り先インスタンスを指定する。
                1.予め送りのオブジェクトにobject_name属性を定義しておく。

                2.指定された名前が存在しない場合self.registry_notify_objects内全てのオブジェクトへ通知される。
            
            notify_to_attr:
                実行する通知先インスタンスのメソッドを指定する。Noneの場合、datamediator_updateが実行される。
                !注意:
                    該当する通知先全てがattr_nameに指定した属性を保有している必要がある。
        '''

        notification_to = kwargs.pop('notification_to', None)
        notify_to_attr = kwargs.pop('notify_to_attr', None)
        instance_list = list()
        debug_logger.debug(f'notify実行')
        debug_logger.debug(f'attr_value: {attr_value}')
        debug_logger.debug(f'self.registry_notify_objects: {self.registry_notify_objects}')
        debug_logger.debug(f'notification_to: {notification_to}')
        debug_logger.debug(f'notify_to_attr: {notify_to_attr}')
        
        if self.registry_notify_objects:
            if notification_to:
                instance_list = self.find_all_notification(notification_to)
                debug_logger.debug(f'notification_to is True')
                debug_logger.debug(f'instance_list: {instance_list}')

            if not instance_list:
                instance_list = self.registry_notify_objects.values()

            for instance in instance_list:
                
                if notify_to_attr and callable(getattr(instance, notify_to_attr, None)):
                    notify_to_attr_method = getattr(instance, notify_to_attr)
                    notify_to_attr_method(attr_value)
                else:
                    instance.datamediator_update(attr_value)



