from collections import deque
import logging
import tracemalloc
from urllib.parse import urlparse
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
#以下新しく追加したwebdrivercontextmanager↓↓↓
from mycrawling.conf import data_setting
from mycrawling.conf.data_setting import ref_dataconfig
#from . import load_use_classes
#from mycrawling.robots.robotfileparse import RobotFileparseManager
#from mycrawling.searchelements.metaelements.attrs_robot import EvalRobotsMetaElements
from mycrawling.utils.imports_module import get_module
from mycrawling.utils.paths import match_urls
#from mycrawling.webdriver_manages.webdriver_manager.chromedriver_manager import ChromeWebDriverContextManager

from mycrawling.logs.debug_log import debug_logger
print(f'data_setting.datamediator: {data_setting.datamediator} (data_setting_mediatorと同じ)')


#Var37.06.14.15a(24/07/25/時点のバージョン)
class MyCrawlingSearch():

    default_datamediator = get_module(ref_dataconfig.get_conf_value('USE_MEDIATOR_PATH'), default=None)#デフォルトで使用するdatamediatorをsettingから取得する。
    CRAWL_DELAY_TIME = ref_dataconfig.get_conf_value('CRAWL_DELAY_TIME', default=5)
    import_classes_parameters = {

    }
    
    debug_logger.debug(f'crawl_delay: {CRAWL_DELAY_TIME}秒')
    def __init__(self, driver_manager, input_url, current_url=None, crawl_delay_time=None, robotmanager=None, **kwargs):
        self.driver_manager = driver_manager
        self.driver = self.driver_manager.driver
        self.driver_wait = self.driver_manager.wait
        self.input_url = input_url
        self.current_url = current_url
        
        datamediator = kwargs.pop('datamediator') if 'datamediator' in kwargs else self.default_datamediator
        self.datamediator = datamediator
        debug_logger.debug(f'DataMediator: {self.datamediator}')
        debug_logger.debug(f'datamediator.dict: {self.datamediator.registry_notify_objects} \n')
        #self.robotmanager新コード
        self.robotmanager = self.datamediator.get_instance('robotfileparse') if not robotmanager else robotmanager

        self.page_evaluation = kwargs.pop('pageevaluation', self.datamediator.get_instance('pageevaluation'))
        self.pageevaluation_parameter = ref_dataconfig.get_conf_value('PAGEEVALUATION_PARAMETER')
        self.datamediator.register_object({'PageEvaluation':self.page_evaluation})

        self.searchanchorelements = kwargs.pop('searchanchorelements', self.datamediator.get_instance('searchanchorelements'))
        self.evaluaterobotsmeta = kwargs.pop('evaluaterobotsmeta', self.datamediator.get_instance('evaluaterobotsmeta'))

        if 'scraping' not in kwargs:
            #scraping_obj = load_use_classes('scrapings', kwargs.pop('scrapings_parameters', None))
            scraping_obj = self.datamediator.get_instance('scraping')
        else:
            scraping_obj = kwargs.pop('scraping')
        self.scraping = scraping_obj
        
        self.time_sleep = crawl_delay_time if crawl_delay_time and isinstance(crawl_delay_time, (int, float)) else self.CRAWL_DELAY_TIME#リクエスト間の待機時間を指定
        self.current_hostname = urlparse(current_url).hostname
        self.is_true_textwords = list()#retain_textwordsから引き継ぐ役割として、「既スクレイピング済ページの再スクレイピング防止」
        self.data_frame = list()
        self.__window_num = 3#変更非推奨。


    @property
    def time_sleep(self):
        return self.__time_sleep
    

    @time_sleep.setter
    def time_sleep(self, crawl_delay):

        if crawl_delay and isinstance(crawl_delay, (int, float)):
            self.__time_sleep = crawl_delay
        else:
            self.__time_sleep = 5


    def get_time_sleep(self, time_sleep_value):
        ''' datamediatorを通した待機時間の取得 '''
        debug_logger.debug(f'get_time_sleep>>>')
        debug_logger.debug(f'time_sleep_value: {time_sleep_value}')
        self.__time_sleep = time_sleep_value


    def datamediator_update(self, value):
        self.is_true_textwords.append(value)
    

    def myscraping(self, *args, **kwargs):
        ''' 全体の実行 '''
        start_time = time.time()
        debug_logger.debug(f'Var37.06.14.3a: 実行')
        #time.sleep(2)
        #raise ConnectionRefusedError#エラー処理実験のみ
        #raise selem_except.TimeoutException
        #raise IndexError
        if self.scraping:
            self.scraping.df = self.data_frame
        robot = self.robotmanager.robots_parse(urls=self.input_url)
        self.time_sleep = getattr(self.robotmanager, 'crawl_delay_time', None)
        debug_logger.debug(f'robot: {robot}')
        if robot:
            logging.info(f'robots_parse():  {robot}')
            self.driver.get(self.input_url)
            self.driver_wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, "*")))
            time.sleep(self.time_sleep)
            self.current_url = self.driver.current_url
            #フォームデータurlが会社概要ページかどうか評価する
            instance_pageevaluation = self.page_evaluation(**self.pageevaluation_parameter)
            if self.evaluaterobotsmeta(self.driver.page_source):
                company_overview = instance_pageevaluation.company_profile(self.driver,
                                                                     self.current_url,
                                                                     **kwargs)#ページが会社概要か評価し要素を返す。            
            else:
                company_overview = list()

            logging.info(f'Scraping実行')
            st = time.time()
            frag = False
            for overview in company_overview:
                if not frag:
                    reference_score_texts = instance_pageevaluation.primary_text_list + instance_pageevaluation.high_score_text_list
                    #reference_score_texts = instance_pageevaluation.retain_textwords
                    debug_logger.debug(f'reference_score_texts:{reference_score_texts}')
                    frag= True
                self.scraping.element_scrape([overview], reference_score_texts)

            logging.info(f'Scraping()実行完了 | time: {time.time() - st}')
            if not self.data_frame:
                self.searchanchorelements.add_visited_urls(self.input_url)
                logging.info(f'searchanchorelements()実行 | ページ探索開始')
                    
                self.searchanchorelements.current_url=self.current_url 
                anchor_urls = self.searchanchorelements(soup_obj=self.driver)
                absolute_href, relative_url = anchor_urls
                debug_logger.debug(f'visited_page: {self.searchanchorelements.visited_page}')
                debug_logger.debug(f'searched_page: {self.searchanchorelements.searched_urls}')
                st = time.time()
                time.sleep(self.time_sleep)
                self.Crawling_pages(absolute_href, relative_url, *args, **kwargs)

                current, peak = tracemalloc.get_traced_memory()
                debug_logger.debug(f'searchanchorelements()実行直後のメモリリソース: current: {current/10**6}MB; peak: {peak/10**6}MB;\n詳細値: current: {current}; peak: {peak}')
                logging.info(f'searchanchorelements()実行完了 | ページ探索終了 | time: {time.time() - st} |')      
        else:
            logging.warning('スクレイピング不可又はrobots.txt参照エラーのサイト')
            self.driver_manager.error_message.append('このサイトはスクレイピング出来ません。')

        if self.robotmanager.error:
            for e in self.robotmanager.error:
                self.driver_manager.error_message.append(e)
        
        if not self.data_frame and not self.driver_manager.error_message:
            self.driver_manager.error_message.append('スクレイピング可能なコンテンツが見つかりませんでした。')

        end_time = time.time()
        if (end_time - start_time) >= 120:
            logging.warning(f'Delayed execution time.許容されるクローリング時間を超過している。| input_url: {self.input_url} | ')
            return


    def __window_handle(self):
        window_num = self.__window_num
        window_handles = self.driver.window_handles
        change_window_num = 2
        if len(window_handles) >= change_window_num:
            if len(window_handles) >= window_num:
                self.driver.switch_to.window(window_handles[0])
                self.driver_wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, "*")))
                time.sleep(1)        
                self.driver.close()
            self.driver.switch_to.window(window_handles[-1])
            self.driver_wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, "*")))
            time.sleep(1)


    def Crawling_pages(self, absol_url:list, rel_url:list,*args, **kwargs):# 右の引数は全てinitにある。'url_prohibition', 'company', 'company_english', 'primary_company', 'primary_company_en'
        """
        formで受け取ったurlページに於いて、search_anchor_elements()で取得したabsolute_hrefのa要素アイテムを一つずつ探索してスクレイピング。
        """
        brakes = False#処理完全終了スイッチ
        absolute_url_list = deque()
        relative_url_list = deque()#対象リンクのwebelementオブジェクト
        jump_page = deque()
        jump_page.append(self.input_url)
        absolute_url_list.append(absol_url)#絶対urlパスのリスト
        relative_url_list.append(rel_url)
        counta = 0#無限ループを防ぐための停止カウンタ
        stop_counta = 20
        start_time = time.time()
        while jump_page and counta <= stop_counta:
            debug_logger.debug(f"jump_page: {jump_page}")
            jump = jump_page.popleft()
            debug_logger.debug(f"absolute_url_list: {absolute_url_list}")
            debug_logger.debug(f'relative_url_list: {relative_url_list}')

            if match_urls(self.driver.current_url, jump) is False:
                self.driver.get(jump)#探索対象のa要素があるページへジャンプ
                self.driver_wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, "*")))#全部表示されるまで待機
                time.sleep(self.time_sleep)

            for relat_href, absol_href in zip(relative_url_list.popleft(), absolute_url_list.popleft()):

                debug_logger.debug(f"jump: {jump} | driver.current_url :{self.driver.current_url}")
                #print(f"absolute_url_list: {absolute_url_list} | : {len(absolute_url_list)}個")
                #print(f'relative_url_list: {relative_url_list} | : {len(relative_url_list)}個')
                debug_logger.debug(f'relat_href: {relat_href} | absol_href: {absol_href}')
                visited_page = self.searchanchorelements.visited_page
                if absol_href in visited_page or relat_href in visited_page:
                    #クロール済みのページはスキップ
                    continue

                elif match_urls(self.driver.current_url, jump) is False:
                    '''ここでもcurrent_url(現在いるurl)が探索対象リンクのあるページか評価 '''
                    self.driver.get(jump)
                    self.driver_wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, "*")))
                    time.sleep(self.time_sleep)

                elm_obj = self.driver.find_element(By.XPATH, f"//a[@href='{relat_href}' or @href='{absol_href}']")
                
                robot = self.robotmanager.robots_parse(urls=absol_href)

                if robot and absol_href != self.driver.current_url:
                    #robots.txtのparse結果且つ参照中のa要素hrefがcurrent_urlで無ければクリック。
                    self.driver.execute_script("arguments[0].click();",elm_obj)#クリックしてページ遷移
                    self.driver_wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, "*")))
                    time.sleep(self.time_sleep)
                    self.__window_handle()#driverのwindow数を調整

                    instance_pageevaluation = self.page_evaluation(**self.pageevaluation_parameter)
                    if self.evaluaterobotsmeta(self.driver.page_source):#meta要素のrobots属性を検証する。
                        company_overview = instance_pageevaluation.company_profile(self.driver,
                                                                               self.driver.current_url,
                                                                               **kwargs)#会社概要ページかチェック
                    else:
                        company_overview = list()
                    
                    frag = False
                    for overview in company_overview:
                        if not frag:
                            #ジェネレータによる遅延評価の為検出されたテキストはここで取得する。
                            reference_score_texts = instance_pageevaluation.primary_text_list + instance_pageevaluation.high_score_text_list
                            debug_logger.debug(f'reference_score_texts:{reference_score_texts}')
                            frag= True
                        self.scraping.element_scrape([overview], reference_score_texts)
                    #会社概要非掲載urlを絶対・相対パス併せて保存
                    self.searchanchorelements.current_url = self.driver.current_url
                    anchor_urls = self.searchanchorelements(soup_obj=self.driver)
                    absolute_href, relative_url = anchor_urls
                    debug_logger.debug(f'visited_page: {self.searchanchorelements.visited_page}')
                    debug_logger.debug(f'searched_page: {self.searchanchorelements.searched_urls}')                    
                    if absolute_href and relative_url:
                        absolute_url_list.append(absolute_href)
                        relative_url_list.append(relative_url)
                        jump_page.append(self.driver.current_url)#リンクリストを取得した場所のurlを格納

                    visited = [self.driver.current_url, absol_href, relat_href]
                    self.searchanchorelements.add_visited_urls(*visited)
                else:
                    continue
                debug_logger.debug(f'経過時間: {time.time() - start_time} 秒')
                if (time.time() - start_time) >= 60:
                    #35秒以上経過していたら終了
                    logging.warning(f'探索タイムオーバー | input_url: {self.input_url} | current_url: {self.driver.current_url}')
                    brakes = True
                    break

            counta += 1
            if brakes:
                break



