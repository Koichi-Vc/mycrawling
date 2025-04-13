from collections.abc import Iterable
from rapidfuzz.distance import Indel
from typing import Union, List, Tuple, Set
from urllib.parse import urljoin
from mycrawling.parse.urlcontentsparse import ParseUrls
from mycrawling.searchelements.element_scorings import ElementsScoring
from mycrawling.scorings.urls import ScoringUrls
from mycrawling.logs.debug_log import debug_logger

#Var37.06.14.15a(24/07/25/時点のバージョン) 

class AnchorElementsScorings(ElementsScoring, ScoringUrls):
    ''' a要素のテキスト、href属性をスコアリングする。 '''
    parseurls = ParseUrls()
    
    def __init__(self, ref_text:Union[List, Tuple, Set]=None, ref_urls=None, **kwargs):
        
        self.__reference_urls = ref_urls
        self.__href_scorer = Indel.normalized_distance
        self.urls_scoring_method = kwargs.pop('urls_scoring_method', self.urls_text_scoring)
        self.select_url_attrs_list = kwargs.pop('select_url_attrs_list', ['path', 'fragment'])#スコアリング対象にするurlsの属性名
        self.href_score_cutoff = kwargs.pop('href_score_cutoff', 0.21)#スコアリング対象のurlsの各属性値スコアの閾値を指定。
        self.href_score_statistics = 'rate'#各属性値スコア,とりわけpathの各urlテキストスコアの統計取得方法
        self.href_statistics_cutoff = kwargs.pop('hrefssocre_sts_cutoff', 60)
        super().__init__(ref_text, **kwargs)


    @property
    def href_scorer(self):
        return self.__href_scorer

    @property
    def reference_urls(self):
        return self.__reference_urls


    @reference_urls.setter
    def reference_urls(self, ref_hrefs):
        if not hasattr(self, 'reference_urls'):
            self.__reference_urls = set()
        
        if isinstance(ref_hrefs, str) or not isinstance(ref_hrefs, Iterable):
            self.__reference_urls.add(ref_hrefs)
        else:    
            for text in ref_hrefs:
                self.__reference_urls.add(text)


    def urls_text_scoring(self, texts, choices, scorer, cutoff, return_score_only=True, *args, **kwargs):
        """ a要素のテキスト・href属性値をスコアリング。 """
        """ ScoringUrlsクラスでurls_text_scoringの戻り値(generator)を展開している。 """
        """
        return_score_only:
            スコア値のみを返す場合はTrue, (score, applicable_txt, txt)で返す場合はFalse
        """
        #スコアのみを返す場合はreturn_score_onlyをTrue
        #戻り値はリスト型又はタプル型リストの二次元配列
        #戻り値データ型はリストの二次元配列

        text_scores = super().urls_text_scoring(texts, choices, scorer, cutoff, *args, **kwargs)
        #a要素リスト全てのテキストコンテンツをスコアリングしリストにまとめる。
        debug_logger.debug(f'text_scores: {text_scores}')
        if return_score_only:
            #スコアのみを返す場合はTrue
            text_scores = text_scores[0] 
        return text_scores



    def urls_scoring(self,
                     urls,
                     scoring_urls_attrs:List[str]=None,
                     select_param=0,
                     **kwargs):
        '''
        scoring_urls_attrs: スコアリング対象にするurlparse属性名 初期値: self.select_url_attrs_list
        '''
        debug_logger.debug(f'urls: {urls}')
        debug_logger.debug(f'scoring_urls_attrs: {scoring_urls_attrs}')
        debug_logger.debug(f'select_param: {select_param}')
        debug_logger.debug(f'kwargs: {kwargs}')
        choices_url_text = self.__reference_urls

        if not scoring_urls_attrs:
            scoring_urls_attrs = self.select_url_attrs_list        
        
        scorer = self.href_scorer
        #引数score_cutoff値を優先し、score_cutoff, href_score_cutoff共にNoneだった場合はNoneをセット。
        score_cutoff = self.href_score_cutoff
        #urlsを解析し、指定した属性値を返す。
        urls_attrs = self.parseurls.get_one_url_attrs(urls, *scoring_urls_attrs)
        scoring_method = self.urls_scoring_method
        #urlsのスコア算出に使うメソッドを指定
        urls_score_list = super().urls_scoring(urls_attrs,
                                               choices_url_text,
                                               scoring_method,
                                               scorer, score_cutoff,**kwargs)
        debug_logger.debug(f'urls_score_list: {urls_score_list}')
        #リスト型の二次元配列が返される為次元を下げる
        for urlscore in urls_score_list:
            statistics_value = self.urls_statistics(urlscore, self.href_score_statistics)
            debug_logger.debug(f'statistics_value:{statistics_value}')

        return statistics_value
    


    def text_and_urls_scoring(self, elements, **kwargs):
        ''' text/href属性値のスコアリング '''
        #scoring_urls_attrs: スコアリング対象にするurlparse属性名 初期値: self.select_url_attrs_list
        #要素からテキスト/href属性値/
        contents = ((elem.text.strip(), elem.get('href')) for elem in elements)
        current_url= kwargs.pop('current_url', '')

        text_score_list = []
        href_score_list = []
        href_list = []
        for text, href in contents:
            text_score = self.best_textcontent_scoring(text, **kwargs)[0]
            absolutepath = urljoin(current_url, href)
            #hrefpath = urlparse(absolutepath).path
            #hrefpath = urlparse(absolutepath)
            #print(f'hrefpath: {hrefpath}')
            hrefs_score = self.urls_scoring(absolutepath,
                                            scoring_urls_attrs=self.select_url_attrs_list,
                                            select_param=0, **kwargs)
            debug_logger.debug(f'text: {text} | text_score: {text_score}')
            debug_logger.debug(f'href: {href} | href_score: {hrefs_score}')
            text_score_list.append(text_score)
            href_score_list.append(hrefs_score)
            href_list.append(href) 
        return text_score_list, href_score_list, href_list


