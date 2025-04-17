from mycrawling.utils.imports_module import get_module
from mycrawling.conf.data_setting import ref_dataconfig


CREATEFILTER_CLS = ref_dataconfig.get_conf_value('CREATEFILTER_CLS', default='')
CREATEFILTERSETS_CLS = ref_dataconfig.get_conf_value('CREATEFILTERSETS_CLS', default='')


class BaseFilterManage():
    ''' 要素検索フィルター用のパラメータハンドラクラスとフィルター作成クラスの管理・インスタンス化、
    を制御する為のインターフェース。
    
    settingファイルからフィルター生成クラスとフィルターセット生成クラスの情報を取得し、ロードする。
    '''
   
    def get_createfilter_cls(self, select_cls_key=None):
        ''' フィルターを作成するクラスをsettingから取得しインポートする。 '''
        #createfilter_cls_nameに何も渡さない場合、メソッドはcreatefilter_cls_name属性を指定しようとする。

        createfilter_cls_obj = None
        createfilter_cls_path = CREATEFILTER_CLS.get(select_cls_key, None)
        if createfilter_cls_path:
            createfilter_cls_obj = get_module(createfilter_cls_path) 
        
        return createfilter_cls_obj
    

    def get_createfilter_classes(self, *select_class_keys):
        ''' 複数のフィルター作成クラスを取得する。select_classesを指定しない場合、settingファイル
        に定義した全てのフィルター作成クラスを取得する。
        '''

        if not select_class_keys:
            select_class_keys = CREATEFILTER_CLS.keys()

        if not hasattr(self, 'createfilter_cls_obj_dict'):
            setattr(self, 'createfilter_cls_obj_dict', dict())

        for key in select_class_keys:
            createfilter_module = self.get_createfilter_cls(key)
            if createfilter_module:
                self.createfilter_cls_obj_dict[key] = createfilter_module

        return self.createfilter_cls_obj_dict


    def has_loaded_createfilter_cls(self, name):
        '''  nameのフィルター生成クラスがインポート済みであるか判定する.24/12/13/追加'''
        result = False
        if not hasattr(self, 'createfilter_cls_obj_dict'):
            #辞書が存在しない場合、一つもインポート出来ていない為Falseを返す。
            return result
        elif name in self.createfilter_cls_obj_dict:
            result = True
        return result


    def get_filterset_cls(self, filterset_cls_name=None):
        ''' フィルターセットを生成するクラスを取得 '''

        if not filterset_cls_name:
            filterset_cls_path = CREATEFILTERSETS_CLS
        else:
            filterset_cls_path = filterset_cls_name
        if filterset_cls_path:
            self.filterset_cls_obj = get_module(filterset_cls_path)

        return self.filterset_cls_obj

    
