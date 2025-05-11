import os
import logging
from urllib.parse import urlparse
import operator
from collections.abc import Iterable
from .elements import ElementsFilter
from rapidfuzz import process as rpdfuzz_process
from rapidfuzz.distance import Indel
from .datas import FilterDataList
from .elements import Processing
import inspect#テスト用
from mycrawling.utils.imports_module import get_module
from mycrawling.logs.debug_log import debug_logger

#from mycrawlingpack.setup import exclude_downloads#後で修正

'''
フィルター生成クラスはあくまでフィルターを生成するオブジェクトである為、属性をはじめとするフィルタリング対象
は別途キーワード引数として用意する。
'''

#Var37.06.14.15a(24/07/25/時点のバージョン)
class AnchorFilterMixin:
    ''' a要素検索フィルターに使う条件式をまとめた。 '''
    
    #preprocessで実装する。
    def exclude_external_urls(self, url):
        ''' href属性値検索対象から外部urlを除外する。 '''

        urls_hostname = urlparse(url).hostname
        return urls_hostname    

    @classmethod
    def exclude_fragment(cls, href_value):
        #href属性に対して使う。
        #フラグメントを検索対象から除外するフィルター
        debug_logger.debug(f'cls: {cls} | href_value: {href_value}')
        return '#' not in href_value


    ''' exclude_dwl_contentsメソッドを実装する場合、以下のプロパティ変数を#1-#3をサブクラスで必ず定義する事。 '''
    #1.
    @property#exclude_dwl_contentsメソッド使用時に参照する拡張子リスト
    def reference_exclude_downloads(self):
        return self.__reference_exclude_downloads


    @reference_exclude_downloads.setter
    def reference_exclude_downloads(self, value):

        if not hasattr(self, 'reference_exclude_downloads'):
            #未だ値がセットされていない場合、空のセットを定義する。
            self.__reference_exclude_downloads = set()
        
        elif not isinstance(self.__reference_exclude_downloads , set):
            raise TypeError('セット型を定義してください')
        
        if not isinstance(value, Iterable):
            value = [value]

        for item in value:

            self.__reference_exclude_downloads.add(item)
        #debug_logger.debug(f'self.__reference_exclude_downloads: {self.__reference_exclude_downloads}')

    #2.    
    @property#exclude_dwl_contentsメソッド使用時に用いるscorer
    def dwlcontents_scorer(self):
        return self.__dwlcontents_scorer
    
    @dwlcontents_scorer.setter
    def dwlcontents_scorer(self, value):
        self.__dwlcontents_scorer = value

    #3.
    @property#exclude_dwl_contentsメソッド使用時に用いるスコア閾値
    def dwlcontents_score_cutoff(self):
        return self.__dwlcontents_score_cutoff

    @dwlcontents_score_cutoff.setter
    def dwlcontents_score_cutoff(self, value):
        if isinstance(value, (int, float)):
            self.__dwlcontents_score_cutoff = value
        else:
            logging.error('値設定に失敗しました。int又はfloat型で指定してください。')
            raise TypeError('正しい値をセットしてください。')

    #hrefを始め, urlやファイルパスを返す属性に対するフィルター
    def exclude_dwl_contents(self, href):
        ''' 拡張子を走査して検索対象からより厳密にダウンロードコンテンツを排除する。 '''
        ''' ※注意
        本メソッドはhref属性のフィルタとして実装する事。
        実装時は、拡張子データを参照するget__reference_exclude_downloadsメソッド、
        socrerを参照するdwlcontents_score_cutoffメソッドを其々定義する事。
        '''
        
        result = False
        exist = None
        hrefsparse = urlparse(href)
        href_path = hrefsparse.path
        file_extention = os.path.splitext(href_path)[-1]
        reference_exclude_downloads = self.reference_exclude_downloads
        dwlcontents_scorer = self.dwlcontents_scorer
        if file_extention:
            exist = rpdfuzz_process.extractOne(
                file_extention,
                reference_exclude_downloads,
                score_cutoff= self.dwlcontents_score_cutoff,
                scorer= dwlcontents_scorer)
        if exist or file_extention == '':
            #拡張子が存在しない場合ダウンロードコンテンツではないと解釈。
            result = True
        return result


#Var37.06.14.15a(24/07/25/時点のバージョン)
class CreateAnchorElementFilter(ElementsFilter, AnchorFilterMixin):
    ''' a要素専用の検索フィルターを作成する。 '''
    '''
    ≪CreateAnchorElementFilterに関するドきゅめんてーション≫24/12/21/
    
    processing:
        フィルターの前後に処理を追加する為のオブジェクト。現在valuefilterメソッドのみでのサポートであり、
        AnchorFilterMixinのメソッドやその他カスタムのフィルタには対応していない。
    '''

    default_exclude_downloads_scorer = Indel.normalized_distance
    processing = Processing()


    def __init__(self, attr=None, value=True, condition= operator.eq, filter_method=None, **kwargs):
        ''' anchor要素用のフィルターメソッド作成クラス '''
        '''
        condition: operatorモジュールがサポートしているオブジェクトを渡す。 
       
        kwargs:
            is_exclude_fragment: False
                フラグメントをフィルターで除外するかをbool型で指定する。デフォルト値はTrueでフラグメントを予め除外する。
                !注意
                有効にする場合は、attr, criteria_value, filter_methodに何も渡されていない様にする必要がある。
                これは用意したフィルター条件やメソッドと常にフラグメントに関するフィルターが重複してしまうのを防ぐためである。
        '''
        
        is_exclude_fragment = bool(kwargs.pop('is_exclude_fragment', False))
        has_attr_and_value = attr and value

        debug_logger.debug(f'filter_method:{filter_method} | kwargs:{kwargs}')
        debug_logger.debug(f'is_exclude_fragment: {is_exclude_fragment}| has_attr_and_value:{has_attr_and_value}')
        
        if filter_method and isinstance(filter_method, str) and '.' in filter_method:
            #インポートパスであると思われる場合はインポートを試みる。
            filter_method = get_module(filter_method)

        if 'exclude_downloads' in kwargs:
            #ダウンロードコンテンツを除外するフィルターを生成する。
            #検索対象から除外する拡張子を指定する。
            self.definition_exclude_downloads(**kwargs)
            if not filter_method:
                filter_method = 'exclude_dwl_contents'       

        if is_exclude_fragment is True and filter_method is None and not has_attr_and_value:
            #フラグメントの除外フィルターを指定する。
            filter_method = 'exclude_fragment'

        
        #フィルターに通す前後プロセスに関する定義を行う。
        affix_methods = kwargs.pop('affix_methods', list())
        if affix_methods and (isinstance(affix_methods, str) or not isinstance(affix_methods, Iterable)):
            affix_methods = [affix_methods]
           
        for method in affix_methods:
            self.processing.affix_methods.append(method)
        self.processing.instance_obj = self

        criteria_value = value#※臨時コード;変数名をvalueからcriteria_valueに変更した為暫くの間互換性を担保する。
        super().__init__(attr, criteria_value, condition, filter_method=filter_method, **kwargs)

    def enable_exclude_fragment(self):
        ''' フラグメントを検索対象から除外するexclude_fragmentメソッドを有効にする。 '''
        return self.set_filter_method('exclude_fragment')    


    def definition_exclude_downloads(self,exclude_downloads, dwl_scorer_cutoff=0.4, **kwargs):
        ''' ダウンロードコンテンツの排除に関するフィルター定義を行う。'''
        self.reference_exclude_downloads = exclude_downloads
        self.dwlcontents_score_cutoff = dwl_scorer_cutoff
        self.dwlcontents_scorer = kwargs.pop('dwlcontents_scorer', self.default_exclude_downloads_scorer)


    #実際にフィルターとして渡すメソッド
    @processing
    def valuefilter(self, element_attr_value, value=None):

        debug_logger.debug(f'self: {self} | element_attr_value: {element_attr_value} | value: {value}')
        return super().valuefilter(element_attr_value, value)

    

    @classmethod
    def filters_factory(cls, attr=None, value=True, condition= operator.eq, filter_method=None,**kwargs):
        ''' 自クラスインスタンスを生成する。 '''
        return cls(attr, value, condition,filter_method, **kwargs)



