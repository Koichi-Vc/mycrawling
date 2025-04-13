from typing import Dict
from mycrawling.conf.data_setting import ref_dataconfig
from mycrawling.searchelements.elements import BaseSearchElements
from mycrawling.utils.imports_module import get_module


#Var37.06.14.15a(24/07/25/時点のバージョン)
class SearchMetaElements(BaseSearchElements):
    default_webdriver = get_module(ref_dataconfig.get_conf_value('USE_WEBDRIVER'))

    def __init__(self, name, attrs_value:Dict = None, filter_method=None, **query_kwargs):
        tag = 'meta'
        if not attrs_value:
            attrs_value = dict()
        attrs_value.setdefault('name', name)#検索するmeta要素のname属性値を指定する。

        super().__init__(tag, attrs_value, filter_method, **query_kwargs)


    def __call__(self, soup_obj, **kwargs):
        kwargs['parse_only_tag'] = 'meta'
        return super().__call__(soup_obj, **kwargs)

