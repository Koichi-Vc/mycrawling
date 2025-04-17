from bs4.element import Tag
import logging
import tracemalloc
from mycrawling.evaluations.evaluationtexts import EvaluateTexts
from mycrawling.parse.elementsparse import ElementsParse
#from mycrawling.crawlings.crawling import MyCrawlingSearch#循環インポート
from mycrawling.conf.data_setting import ref_dataconfig
from mycrawling.utils.imports_module import get_module
from mycrawling.logs.debug_log import debug_logger



#Var37.06.14.15a(24/07/25/時点のバージョン)
class PageEvaluation(EvaluateTexts):
    ''' search_sys_dev.ipynbより「find_all(True)の後のフィルター機能の開発　クラス var2」を採用'''

    is_true_urls = set()#searchanchorelementsインスタンスによるurl単独のスコアリング評価でTrue判定を受けたurlの絶対パスセットを保持。
    default_notify_to_obj_name = 'crawling_class'
    default_webdriver = get_module(ref_dataconfig.get_conf_value('USE_WEBDRIVER'), None)

    def __init__(self, evaluate_reference_textsets=None, reference_title_a_url_texts=None, **kwargs):
        datamediator = kwargs.pop('datamediator', get_module(ref_dataconfig.get_conf_value('USE_MEDIATOR_PATH', default='')))
        
        if isinstance(datamediator, str):
            self.datamediator = get_module(datamediator)
        else:
            self.datamediator = datamediator
        webdriver = kwargs.get('webdriver', self.default_webdriver)
        self.parse_elements = ElementsParse(webdriver=webdriver) if 'elementparse' not in kwargs.keys() else kwargs.get('elementparse')
        self.traverse_for_root_element = 'body'#最初にページ全体の走査をする際にルート要素とするタグの指定。
        self.pagescorings = None
        if 'pagescorings' in kwargs.keys():
            self.pagescorings = kwargs.get('pagescorings')
        elif hasattr(self, 'datamediator'):
            self.pagescorings = self.datamediator.get_instance('pagescorings')

        debug_logger.debug(f'evaluate_reference_textsets: {evaluate_reference_textsets}')
        debug_logger.debug(f'reference_title_a_url_texts: {reference_title_a_url_texts}')
        
        #コンテンツの評価に用いる条件
        #必要なコンテンツ内子要素の数
        self.reqd_child_count = 4
        #必要な重要,高類似度テキストの種類数
        self.reqd_detection_primary_texts = 3
        self.reqd_detection_highscore_texts = 4
        #必要な重要,高類似度テキスト数
        self.reqd_primary_texts_count = 4
        self.reqd_highscore_texts_count = 5
        self.reqd_all_high_score_rate = 40
        self.high_score_jp_text = []#言語別に収集した高類似度テキスト。※現状未使用
        self.high_score_en_text = []#言語別に収集した高類似度テキスト。※現状未使用
        self.high_score_text_list = list()#ルート要素上から検出した高類似度テキスト
        self.primary_text_list = list()#ルート要素上から検出した重要語彙テキスト
        self.notify_to_obj_name = self.default_notify_to_obj_name if 'notify_to_obj_name' not in kwargs.keys() else kwargs.pop('notify_to_obj_name')
        #obj_name = TestAssistance#オフラインテスト用
        get_attr_name = 'is_true_textwords'
        true_textwords = self.datamediator.get_attr(self.notify_to_obj_name, get_attr_name)        
        #MyCrawlingSearchインスタンスが保持している既出の高類似度テキストコンテンツリストを参照する。
        self.is_true_textwords = true_textwords if true_textwords else list()
        self.is_true_textwords_notification_to = kwargs.pop('is_true_textwords_notification_to', self.notify_to_obj_name)

    @classmethod
    def datamediator_update(cls, value):
        cls.is_true_urls = value
        debug_logger.debug(f'cls.is_true_urls: {cls.is_true_urls}')
    

    def condition_evaluation_beta(self, 
                                   eval_primary_text_types,
                                   eval_highscore_text_types,
                                   eval_primary_text_count,
                                   eval_highscore_text_count,
                                   eval_primary_or_highscore_text_count,
                                   eval_all_high_score_rate):
        ''' 評価した数値をもとに統計を取り、対象要素オブジェクトかどうか条件判定する '''
        debug_logger.debug(f'eval_primary_text_count: {eval_primary_text_count} | eval_highscore_text_count : {eval_highscore_text_count}')
        result = False

        if eval_primary_or_highscore_text_count and eval_all_high_score_rate:#その要素に属する子要素の必要数を前提にする。

            if eval_primary_text_types and eval_highscore_text_types:
                #重要語彙の種類数 and 高類似度語彙の種類数で条件評価
                result = True

            elif eval_primary_text_count and eval_highscore_text_count:
                #検出された重要語彙の数 and 高類似度語彙の数で条件評価
                result = True

            elif eval_primary_text_types and eval_primary_text_count:
                #検出された重要語彙の種類数 and 数で条件評価
                result = True

            elif eval_highscore_text_count and eval_all_high_score_rate:
                #高類似度語彙の数 and 子要素数に対する全高類似度語彙の割合で条件評価
                result = True

            debug_logger.debug(f'eval_primary_text_types: {eval_primary_text_types} | eval_highscore_text_types: {eval_highscore_text_types}')
            debug_logger.debug(f'eval_primary_text_count: {eval_primary_text_count} | eval_highscore_text_count: {eval_highscore_text_count}')
            debug_logger.debug(f'eval_all_high_score_rate: {eval_all_high_score_rate}')

        return result


    def find_overview_elements(self, soup_obj):
        ''' htmlページ全体から対象コンテンツが存在するか走査する。 '''

        result = False
        exclude_tags = {'html'}
        pry_and_hhscore_texts = []#ページ解析と走査で収集したprimaryとhigh_scoreテキストのリスト
        root_element = soup_obj.find([self.traverse_for_root_element])#ルート要素又は文書本体要素の検索を試みる
        elements = None
        debug_logger.debug(f'root_element: {root_element} | {len(root_element)} | {root_element.name}')

        if root_element:
            #ルート要素から対象テキスト全てを検出する。
            self.primary_text_list, self.high_score_text_list = self.pagescorings.detect_high_score_texts(root_element)  
            pry_and_hhscore_texts = self.high_score_text_list + self.primary_text_list

            debug_logger.debug(f'high_score_text_list : {self.high_score_text_list}')
            debug_logger.debug(f'primary_text_list : {self.primary_text_list}')
            debug_logger.debug(f'self.is_true_textwords: { self.is_true_textwords}')
            debug_logger.debug(f'pry_and_hhscore_texts: {pry_and_hhscore_texts}')
            if (len(self.high_score_text_list) >= 3 or len(self.primary_text_list) >= 2) and pry_and_hhscore_texts not in self.is_true_textwords:
                debug_logger.debug(f'high_score_search True')
                
                elements = [elm for elm in root_element.find_all(lambda element: element.name not in exclude_tags)]
                notification_to = 'MyCrawlingSearch'
                notification_to = 'testassistance'#オフラインテスト用
                self.datamediator.notify(
                    pry_and_hhscore_texts,
                    notification_to= self.is_true_textwords_notification_to
                    )
        
        if elements:
            #対象テキスト検出, 要素が取得出来たら走査を開始する。
            for element in elements:
                if isinstance(element, Tag):
                    
                    detection_texts_obj = self.pagescorings.child_elements_traverse_beta(element)
                    if detection_texts_obj is not None:
                        evaluated_statistics = detection_texts_obj.text_score_statistics_eval(self)
                        reqd_condition_evaluation_beta_parametor = 6
                        if not len(evaluated_statistics) >= reqd_condition_evaluation_beta_parametor:
                            continue
                        result = self.condition_evaluation_beta(*evaluated_statistics.values())
                    else:
                        result = False
                    
                    if result:
                        debug_logger.debug(f'element: {element}')
                        debug_logger.debug(f'elements texts: {[e.text for e in element]}')

                        length_contents = len([content for content in element.contents if content.name != None])
                        targ_contents_rate = 85

                        debug_logger.debug(f'elementのdl要素数: {len(element.find_all("dl"))} | element.contents: {len(element.contents)} | length_contents: {length_contents}')
                        
                        if len(element.find_all('dl')) / length_contents*100 >= targ_contents_rate:
                            element.attrs['class'] = 'overview_dl_elements'
                        yield element                   
                

    def company_profile(self,
                        driver,
                        current_url,
                        **kwargs): 
        """
        ページが会社概要ページかどうかを検査する。ページ内でリンクのない会社概要に関する項目テキストを返す。
        compay: 会社概要を構成する項目キーワードのリスト(会社概要キーワード)
        """
        debug_logger.debug(f'kwargs: {kwargs}')
        debug_logger.debug(f'is_true_urls {self.is_true_urls}')
        is_contain = None
        similar_url = None
        similar_title = None
        soup = self.parse_elements.element_parse(driver)#obj_parser⇒self
        title_score, title_text, is_contain = self.pagescorings.scoring_titles(soup_obj=soup)
       
        debug_logger.debug(f'title_text: {title_text} | title_score: {title_score}')
        similar_title = title_score
        similar_url = current_url in self.is_true_urls
        similar_title = similar_title is not None 
        #タイトル要素のスコアリングだけ判断するには限界がある。24/04/29
        
        debug_logger.debug(f'similar_title:{similar_title} | is_contain: {is_contain} | similar_url: {similar_url}')
        similar_title_url = similar_title or is_contain or similar_url
        if similar_title_url:
            ''' trimming()後にオブジェクトが有り且つページtitle, urlの評価スコアを参照 '''
            logging.info(f'similar_title_url == True')
            
            debug_logger.debug(f'kwargs: {kwargs}')
            elements = self.find_overview_elements(soup)
            
            for element in elements:
                debug_logger.debug(f'yield element: {element} | True')
                yield element
            current, peak = tracemalloc.get_traced_memory()
            debug_logger.debug(f'company_profile()for文内のメモリリソース: current: {current/10**6}MB; peak: {peak/10**6}MB;\n詳細値: current: {current}; peak: {peak}')
            logging.info(f'MemoryResource: current: {current/10**6}MB; peak: {peak/10**6}MB |')             


