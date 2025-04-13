from collections.abc import Iterable
from urllib.parse import urlparse, urljoin
from mycrawling.conf.data_setting import ref_dataconfig
from mycrawling.evaluations.evaluationurls import EvaluateUrls
from mycrawling.utils.imports_module import get_module
from .scoring import AnchorElementsScorings
from mycrawling.logs.debug_log import debug_logger

#Var37.06.14.15a(24/07/25/時点のバージョン)
class EvaluateAnchorElements(EvaluateUrls):
    ''' a要素のテキストコンテンツ・href属性値をスコアリング・評価する。 '''

    default_parameter = ref_dataconfig.get_conf_value('EVALUATEANCHORELEMENTS_PARAMETERS', default=None)
    
    def __init__(self, ref_text=None, ref_urls=None, **kwargs):
        #print(f'reference_texts: {reference_texts} | reference_urls: {reference_urls}')
        self.datamediator = kwargs.pop('datamediator', get_module(ref_dataconfig.get_conf_value('USE_MEDIATOR_PATH')))
        
        if self.datamediator and not ref_text or not ref_urls:         
            ref_text = self.datamediator.get_attr('reference_title_a_url_texts', 'reference_texts')
            ref_urls = self.datamediator.get_attr('reference_title_a_url_texts', 'reference_urls')
        
        anchor_elements_scoring = kwargs.pop('anchor_elements_scoring', None)
        self.anchor_elements_scoring = AnchorElementsScorings(ref_text=ref_text, ref_urls=ref_urls) if not anchor_elements_scoring else anchor_elements_scoring
        debug_logger.debug(f'datamediator: {self.datamediator}')
        self.is_true_url_set = set()#urlパス自体の評価がTrue判定になったurlを絶対パスで保持
        self.is_true_url_set_notify_to = 'pageevaluation'


    #get_is_true_url_setの後継
    @property
    def is_true_url_set(self):
        return self.__is_true_url_set
    

    @is_true_url_set.setter
    def is_true_url_set(self, values):

        if not hasattr(self, 'is_true_url_set'):
            self.__is_true_url_set = set()
            return 

        if isinstance(values, str) or not isinstance(values, Iterable):
            self.__is_true_url_set.add(values)
        else:
            for value in values:
                self.__is_true_url_set.add(value)

        if self.datamediator:
            self.datamediator.notify(
                self.__is_true_url_set,
                notification_to= self.is_true_url_set_notify_to
                )

    @classmethod
    def create_instance(cls, *args, **kwargs):
        if args or kwargs:
            return cls(*args, **kwargs)
        elif cls.default_parameter:
            return cls(**cls.default_parameter)
        else:
            return cls()
        

    def del_item_is_true_url_set(self, *items):
        for item in items:
            if item in self.__is_true_url_set:
                self.__is_true_url_set.discard(item)

    
    def evaluate_text_and_href(self,
                               elements,
                               current_url:str,
                               **kwargs
                               ):
        ''' text_and_urls_scoringで算出されたスコアを元にテキスト/href属性値を評価する。 '''
        #current_urlは、現在アクティブになっているurlを受け取る。
        
        #url_scoring_type = kwargs.pop('url_scoring_type', 'all')
        text_score_list, href_score_list, href_list = self.anchor_elements_scoring.text_and_urls_scoring(elements, current_url=current_url, **kwargs)
        debug_logger.debug(f'text_score_list: {text_score_list}')
        debug_logger.debug(f'href_score_list:{href_score_list}')
        debug_logger.debug(f'href_list: {href_list}')

        urls_boudary = self.anchor_elements_scoring.href_statistics_cutoff
        #算出した各テキスト/hrefのスコアを評価する
        counta = 0#テスト用
        for text_score, hrefs_score, href_value in zip(*[text_score_list,href_score_list,href_list]):
            counta += 1
            
            debug_logger.debug(f'text_score: {text_score}')
            debug_logger.debug(f'hrefs_score: {hrefs_score}')
            debug_logger.debug(f'href_value: {href_value}')

            hostname_is_current_hostname = self.evaluate_hostname(
                current_url, href_value)#href属性値がサイト内urlか評価する。
            debug_logger.debug(f'hostname_is: {hostname_is_current_hostname} | href_value: {href_value}')
            evaluated_hrefs = self.evaluate_score(scorer_type='Wratio',
                                                  score=hrefs_score,
                                                  name_is_current_name=hostname_is_current_hostname,
                                                  boundary=urls_boudary,
                                                  **kwargs)
            #テキストコンテンツのスコア評価と
            #テキストコンテンツ/href属性値の何方か一方の評価が通れば返す。
            if text_score is not None or evaluated_hrefs is True:
                
                url_hostname = urlparse(href_value).hostname
                #href属性値から絶対urlパス/相対urlパスを生成して返す。
                if url_hostname is None:
                    absol_href = urljoin(current_url, href_value)
                    rel_href = href_value
                else:
                    absol_href = href_value
                    rel_href = href_value
                    
                if evaluated_hrefs is True:
                    debug_logger.debug(f'evaluated_hrefs: {evaluated_hrefs}')
                    self.is_true_url_set = absol_href
                yield absol_href, rel_href


