from collections import deque
import logging
from urllib.parse import urlparse
from typing import Dict, List
from types import GeneratorType
from mycrawling.searchelements.elements import BaseSearchElements
from ..filters import SearchElementFilterManager
from .evaluation import EvaluateAnchorElements
from mycrawling.conf.data_setting import ref_dataconfig
from mycrawling.utils.imports_module import get_module
from mycrawling.logs.debug_log import debug_logger


#Var37.06.14.15a(24/07/25/時点のバージョン)
class SearchAnchorElements(BaseSearchElements):
    ''' a要素を検索する為のクラス
    '''
    default_filter_class_key = 'a'#FilterManagerに於いてフィルタークラスを管理しているキー
    #default_evaluate_object = ref_dataconfig.get_conf_value('USE_CLASSES', 'evaluateanchorelements')
    default_evaluate_object = EvaluateAnchorElements
    #default_evaluate_object = None
    default_webdriver = get_module(ref_dataconfig.get_conf_value('USE_WEBDRIVER'))
    #datamediator = get_module(ref_dataconfig.get_conf_value('USE_MEDIATOR_PATH'))#やっぱり使わないかも。

    def __init__(self,
                 attrs_value:Dict = None,
                 string=None,
                 current_url=None,
                 current_hostname = None,
                 evaluate_objects= None,
                 handling_fragment=False,
                 filtermanager=None,
                 **query_kwargs):
        '''
        args:
            evaluate_objects:
                a要素のテキスト、href属性値を評価するクラスを受けとる。
            evaluate_parameters:
                evaluate_objectsをインスタンス化する為のパラメータを受けとる。デフォルト値はNone
        '''

        tag ='a'
        if attrs_value is None:
            attrs_value = dict()
        self.current_url = current_url#※urlはページ訪問毎に更新される。
        self.current_hostname = current_hostname if current_hostname else urlparse(self.current_url).hostname
        self.searched_urls = set()#検索済みurlの保持
        self.visited_page = set()#クロール訪問済みのurlを保持
        self.filter_class_key = query_kwargs.pop('filter_class_key', self.default_filter_class_key)

        #if-elifの修正
        if not evaluate_objects:
            self.evaluate_objects = self.default_evaluate_object.create_instance()

        #評価クラス新コードここまで。
        debug_logger.debug(f'self.evaluate_objects : {self.evaluate_objects } | evaluate_objects: {evaluate_objects}')
        
        self.filtermanager = filtermanager
        if not callable(filtermanager) and not attrs_value and not string:
            self.filtermanager = SearchElementFilterManager
        elif isinstance(filtermanager, str) and not attrs_value and not string:
            self.filtermanager = get_module(filtermanager)

        self.handling_fragment = handling_fragment

        #filtermanageの新コード
        if self.filtermanager:
            filters = self.filtermanager.create_filter(tag, self.filter_class_key)
            attrs_value.update(filters)
            debug_logger.debug(f'filters: {filters} | attrs_value: {attrs_value}')

        debug_logger.debug(f'query_kwargs: {query_kwargs}')
        super().__init__(tag, attrs_value, string, **query_kwargs)


    def __call__(self, soup_obj):
        parse_only_tag = 'a'#beautifulsoup解析対象をa要素に絞る。
        elements = super().__call__(soup_obj, parse_only_tag=parse_only_tag)
        debug_logger.debug('__call__実行完了')
        debug_logger.debug(f'elements: {elements}')


        if self.handling_fragment:
            #フラグメントを含めない場合
            elements = self.exclude_fragment(elements)

        elements = self.exclude_rel_attr_nofollow(elements)#rel属性値のnofollowを除外する。※ロボット制御に関連する為。
        evaluated_elements = self.evaluate_objects.evaluate_text_and_href(
            elements,
            current_url=self.current_url
        )
        #print(f'evaluated_elements: {}')
        evaluated_href_values = self.return_evaluated_urls(evaluated_elements)
        debug_logger.debug(f'evaluated_href_values: {evaluated_href_values} | searched_url: {self.searched_urls} | visited_page: {self.visited_page}') 
        return evaluated_href_values     


    @property
    def current_url(self):
        return self.__current_url
    
    @current_url.setter
    def current_url(self, url):
        self.__current_url = url
        host = urlparse(url).hostname
        if not hasattr(self, 'current_hostname') or host and host != self.current_hostname:
            debug_logger.debug(f'set current_hostname, host: {host}')
            self.current_hostname = host


    @property
    def current_hostname(self):
        debug_logger.debug(f'current_hostname: {self.__current_hostname}')
        return self.__current_hostname


    @current_hostname.setter
    def current_hostname(self, host):
        self.__current_hostname = host

    @property
    def handling_fragment(self):
        #フラグメントの扱いを指定する。
        return self._handling_fragment
    
    @handling_fragment.setter
    def handling_fragment(self, value):
        if not isinstance(value, bool):
            raise TypeError('bool型のみを受けとります。')
        elif not hasattr(self, 'handling_fragment'):
            self._handling_fragment = False
        
        self._handling_fragment = value


    def exclude_fragment(self, elements):
        #フラグメントを除外するメソッド
        
        for element in elements:
            href_value = element.get('href', None)
            debug_logger.debug(f'href_value: {href_value}')
            if not href_value or (href_value and "#" not in href_value):
                debug_logger.debug(f'if-True, href_value: {href_value}')

                yield element

    def exclude_rel_attr_nofollow(self, elements):
        #rel属性値がnofollowの要素を除外する。
        for element in elements:
            rel_value = element.get('rel', None)
            if not rel_value or (rel_value and 'nofollow' not in rel_value):
                yield element

    #廃止する方向で。
    def get_evaluate_class(self, cls_name):
        ''' 検索した要素の評価を行うクラスを設定情報から取得し、evaluate_objectsに設定する。 '''
        cls_path = None
        if hasattr(ref_dataconfig, 'get_class_obj'):
            cls_path = ref_dataconfig.get_conf_value('USE_CLASSES', cls_name)
            self.evaluate_objects = get_module(cls_path)

        return self.evaluate_objects


    def add_searched_urls(self, *searched_url):
        ''' 検索・抽出済みのurlを追加する。'''
        for url in searched_url:
            self.searched_urls.add(url)


    def add_visited_urls(self, *visited_url):
        for url in visited_url:
            self.visited_page.add(url)


    def return_evaluated_urls(self, url_items:List[List[str]], *other_exclude_elements):
        '''
        検索したhref値(絶対url/相対urlパス)を返す。href値・テキストにより返すアイテムを除外する場合は、
        other_exclude_elementsを指定する。
        '''
        ''' urls_itemsには二次元配列で[absolute, relative]のペアリストを渡す。 ''' 
        list_length = 1

        if not isinstance(url_items, (list, tuple, deque, GeneratorType)):
            url_items = [url_items]
        
        debug_logger.debug(f'url_items: {url_items}')
        absolute = []
        relative = []
        for urls in url_items:
            debug_logger.debug(f'urls:{urls}')
            if len(urls) <= list_length:
                logging.error('絶対url/相対urlパスの両方が必要です。')
                absolute, relative = None, None
                return absolute, relative
            
            absol, rel = urls
            yet_to_searched = rel not in self.searched_urls and absol not in self.searched_urls
            yet_to_visited = rel not in self.visited_page and absol not in self.visited_page
            
            if yet_to_searched is True and yet_to_visited is True:
                #未検索 and 身訪問のurlの場合追加する。
                searched_urls = [absol, rel]
                self.add_searched_urls(*searched_urls)
                relative.append(rel)
                absolute.append(absol)

        return absolute, relative


    #find_elementsメソッドのベータ版、
    #__call__が担う場合不要になる可能性あり
    #__call__を使わない場合でも内部タスクは大幅に削減される。
    def find_elements(self,
                           soup_obj,
                           current_url=None):
        ''' find_elementsメソッドのオーバーライド '''
        elements = super().find_elements(soup_obj)
        if current_url is None:
            current_url = self.current_url
        #elementsを返したら、評価に移る。
        evaluated_elements = self.evaluate_objects.evaluate_text_and_href(
            elements,
            current_url=current_url
        )
        evaluated_href_values = self.return_evaluated_urls(evaluated_elements)

        return evaluated_href_values


