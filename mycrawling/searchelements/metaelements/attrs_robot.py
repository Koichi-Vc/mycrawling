from collections.abc import Iterable
from typing import Dict, List
from .metaelements import SearchMetaElements
from mycrawling.logs.debug_log import debug_logger

#Var37.06.14.15a(24/07/25/時点のバージョン)

#Attr_RobotMetaElements_Parseから改名
class Attr_RobotsMetaElements_Parse(SearchMetaElements):
    ''' meta要素からname robotsを検索し、指示を解析する。 '''
    '''
    注釈: instraction == instr
    '''
    default_re_instr_allow_list = ['follow','index', 'all']
    default_re_instr_disallow_list = ['noindex','nofollow', 'none']

    def __init__(self, attrs_value: Dict = None, filter_method=None, re_instr_disallow_list=None, re_instr_allow_list=None, **query_kwargs):
        name = 'robots'
        #attrs_value.setdefault('name', 'robots')
        self.detect_instraction_to_robots = set()#検出されたロボットへの指示を格納。

        self.re_instr_disallow_list = self.default_re_instr_disallow_list if re_instr_disallow_list is not None else list()#robotsの禁止を意味する参照値を保持
        self.re_instr_allow_list = self.default_re_instr_allow_list if not re_instr_allow_list else re_instr_allow_list#robotsの許可を意味する参照値を保持

        super().__init__(name, attrs_value, filter_method, **query_kwargs)


    def detect_instraction(self, elements):
        ''' 検索結果からcontents属性値を抽出し、robotへの命令を取得する。 '''        
        for element in elements:
            content = element.get('content')
            debug_logger.debug(f'elements content: {content}')
            content_values = content.split(',')#","区切りで複数指定されている場合を想定してsplitを掛けておく。
            if content_values:
                for value in content_values:
                    self.detect_instraction_to_robots.add(value)
        return self.detect_instraction_to_robots
    
    
    def eval_instraction_to_robots(self, re_instr_disallow_list:List[str]=None, **kwargs):
        ''' 検出されたmeta robotsに対する指示(content)を評価する。'''
        contain_instraction = dict()#含まれていた指示
        detect_instraction_to_robots = kwargs.pop('detect_instraction_to_robots', self.detect_instraction_to_robots)
        re_instr_disallow_list = re_instr_disallow_list if re_instr_disallow_list else self.re_instr_disallow_list
        result = False
        
        for detect_instr in detect_instraction_to_robots:

            if detect_instr in self.re_instr_allow_list or detect_instr not in re_instr_disallow_list:
                result = True
            contain_instraction[detect_instr] = result

        return contain_instraction


    def is_allowing_robots(self, contain_instraction:List):
        ''' bool型アイテムリストのrobots許可を評価する。 '''

        debug_logger.debug(f'contain_instraction: {contain_instraction}')
        if not isinstance(contain_instraction, str) and isinstance(contain_instraction, Iterable):
            result = any(contain_instraction) if len(contain_instraction) != 0 else True
        else:
            raise TypeError(f'処理できないデータ型です. contain_instraction: {contain_instraction}')
        return result

class EvalRobotsMetaElements(Attr_RobotsMetaElements_Parse):

    def __init__(self, attrs_value = None, filter_method=None, re_instr_disallow_list=None, re_instr_allow_list=None, **query_kwargs):
        super().__init__(attrs_value, filter_method, re_instr_disallow_list, re_instr_allow_list, **query_kwargs)


    def __call__(self, soup_obj, **kwargs):
        elements = super().__call__(soup_obj, **kwargs)
        
        self.detect_instraction_to_robots = self.detect_instraction(elements)#meta
        contain_instraction = self.eval_instraction_to_robots()
        return self.is_allowing_robots(contain_instraction.items())
    

