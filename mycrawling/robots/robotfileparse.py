import logging
import requests
import time
from urllib.parse import urlparse
from mycrawling.conf.data_setting import ref_dataconfig
from mycrawling.utils.imports_module import get_module
from mycrawling.logs.debug_log import debug_logger


#Var37.06.14.15a(24/07/25/時点のバージョン)
class RobotFileparseManager():
    ''' robots.txtファイルの解析を行う '''
    #default_logging_formatter = '%(asctime)s | %(created)s | %(name)s | %(levelname)s | robots_url: %(robots_url)s | %(message)s | '

    conf_message_val = 'ROBOTS_ERROR_MESSAGE_DICT'

    def __init__(self, rp=None, useragent='*', prohibition_url_list=None, optional_data_obj=None, custom_message_dict=None, **kwargs):

        self.parse_dict = {}#parse済み辞書型コレクション
        self.format_extra = dict()
        self.robots_url = None
        self.__crawl_delay_time = None#新しく追加(24/06/27)
        #コンストラクタ実引数の処理
        self.rp = rp
        self.useragent = useragent
        self.request_check_timeout = kwargs.get('request_check_timeout', 6)
        self.prohibition_url_list = prohibition_url_list if prohibition_url_list is not None else list() 
        self.optional_data_obj = optional_data_obj
        self.custom_message_dict = custom_message_dict
        self.kwargs = kwargs
        debug_logger.debug(f'kwargs: {kwargs}')
        if not self.rp:#RobotFileParserオブジェクトが指定されていない場合、設定オブジェクトの内容を優先して適用する。
            parameters = ref_dataconfig.get_conf_value('ROBOTFILEPARSE_PARAMETER')
            debug_logger.debug(f'parameters:{parameters}')
            for param_name, value in parameters.items():
                obj = None
                
                if isinstance(value, str) and '.' in value:
                    obj = get_module(value)
                    if param_name == 'rp' and callable(obj) and 'rp_parameter' in kwargs:
                        rp_parameter = kwargs.get('rp_parameter')
                        obj = obj(**rp_parameter)
                    elif param_name == 'rp' and callable(obj):
                        obj = obj()

                if obj:
                    setattr(self, param_name, obj)
                else:
                    setattr(self, param_name, value)
        
            match hasattr(self, 'datamediator'):
                case False if 'datamediator' in self.kwargs.keys():
                    self.datamediator = self.kwargs.pop('datamediator')
                case False:
                    self.datamediator = get_module(ref_dataconfig.get_conf_value('USE_MEDIATOR_PATH'))

        if not self.prohibition_url_list:

            if hasattr(optional_data_obj, 'prohibition_url_list'):
                self.prohibition_url_list = getattr(optional_data_obj, 'prohibition_url_list')

            elif hasattr(self, 'datamediator') and self.datamediator.has_registry_obj('robotsparsedatalist'):
                prohibition_url_list = self.datamediator.get_attr('robotsparsedatalist', 'prohibition_url_list')
                self.prohibition_url_list = prohibition_url_list if prohibition_url_list else list()

        elif hasattr(self.prohibition_url_list, 'prohibition_url_list'):
            self.prohibition_url_list = getattr(self.prohibition_url_list, 'prohibition_url_list')

        
        match hasattr(self, 'error_loghandling_obj'):

            case True if ref_dataconfig.has_config('ROBOTS_ERRORLOGHANDLING_PARAMETERS'):
                ROBOTS_ERRORLOGHANDLING_PARAMETERS = ref_dataconfig.get_conf_value('ROBOTS_ERRORLOGHANDLING_PARAMETERS')
                self.error_loghandling_obj = self.error_loghandling_obj(**ROBOTS_ERRORLOGHANDLING_PARAMETERS)
            
            case True if self.custom_message_dict:
                setattr(self.error_loghandling_obj, 'custom_message_dict', custom_message_dict)
        
        if hasattr(self, 'error_loghandling_obj') and callable(self.error_loghandling_obj):
            self.request_check = self.error_loghandling_obj(self.request_check)

        self.result = False
        self.error = ''
        self.domain_host = None
        self.notify_to_instance = kwargs.pop('notify_to_instance', None)#通知先インスタンスを指定
        self.select_notify_attr = kwargs.pop('select_notify_attr', 'crawl_delay_time')#通知先インスタンスへ通知するオブジェクトを指定する。
        if not hasattr(self, 'notify_to_attr'):
            self.notify_to_attr = kwargs.pop('notify_to_attr', None)#呼び出す通知先インスタンスのメソッドを指定

    @property
    def robots_url(self):

        return self.__robots_url
    
    @robots_url.setter
    def robots_url(self, url_value):
        self.__robots_url = url_value

        format_exc_robots = self.format_extra.get('robots_url', None)
        if not format_exc_robots or format_exc_robots != url_value:
            self.format_extra['robots_url'] = url_value

    @property
    def crawl_delay_time(self):
        #クローリングの待機時間を取得する。
        return self.__crawl_delay_time


    @crawl_delay_time.setter
    def crawl_delay_time(self, delay_time):

        self.__crawl_delay_time = delay_time

        if self.datamediator and self.select_notify_attr == 'crawl_delay_time' and self.notify_to_instance:
            debug_logger.debug(f'notify実行')
            self.datamediator.notify(delay_time,
                                     notification_to=self.notify_to_instance,
                                     notify_to_attr=self.notify_to_attr)

    
    def get_prohibition_url_list(self):
        ''' スクレイピング禁止urlを取得する。'''
        prohibition_url_list = self.datamediator.get_conf_value('robotsparsedatalist')


    def url_extract(self, urls):
        ''' urlをparseし、domainを抽出、robots.txtへのパスを生成 '''

        parsed_url, domain, domain_name, robots_url = None, None, None, None

        if not urls:
            parsed_url = '値が有りません'
            return parsed_url, domain, domain_name, robots_url
        #urls = quote(urls, safe=':/')
        parsed_url = urlparse(urls)#parseしたurlsを格納
        domain_name = parsed_url.hostname
        debug_logger.debug(f'domain_name: {domain_name}')
        domain = parsed_url.scheme + '://' + domain_name
        robots_url = domain + '/robots.txt'
                #　↓元々urlsを返していた
        return parsed_url, domain, domain_name, robots_url


    #@Errorloghandlings_Class(custom_message_dict=conf_message_val, logger_conf_variable='ROBOTS_SETUP_LOGGER')
    def request_check(self, robots_url):#実験時はrobots_urlはselfのアノテーション化してエスケープする事。
        ''' robots.txtファイルへの参照が可能か評価'''
        debug_logger.debug(f'self: {self} | robots_urls: {robots_url}')
        session = False
        self.robots_url = robots_url#実験時はコメントアウト
        #raise requests.exceptions.Timeout
        response = requests.get(self.robots_url, timeout=self.request_check_timeout)
        response.raise_for_status()
        time.sleep(1)

        if response:
            session = True
        return session


    def set_url_fetch(self, urls, robots_url):
        ''' robots.txtパスをセットして参照・urlへの訪問許可を評価 '''
        if self.result:#アクセスを予めFalseに初期化しておく
            self.result = False
        self.rp.set_url(robots_url)
        time.sleep(1)
        self.rp.read()
        time.sleep(1)
        self.result =self.rp.can_fetch(self.useragent, urls)
        self.__crawl_delay_time = self.rp.crawl_delay('*')

        if urls not in self.parse_dict:
            self.parse_dict[urls] = self.result
        return self.result


    def robots_parse(self, urls):
        self.result = False#アクセスを予めFalseに初期化しておく
        seturl_switch = False#robot.txtファイルの参照実行スイッチ
        if urls == '値が有りません':
            self.result = False
            self.error = 'urlが入力されていない可能性があります。'
            return self.result
        
        parsed_url, domain, domain_name , robots_url = self.url_extract(urls)
        debug_logger.debug(f'parsed_url: {parsed_url} | domain: {domain} | domain_name: {domain_name} | robots_url: {robots_url}')
        debug_logger.debug(f'any:  {any(name for name in self.prohibition_url_list if not domain_name in name)}')
        
        is_prohibition_url = any(name for name in self.prohibition_url_list if domain_name in name)#クロール/スクレイピング禁止サイト判定
        
        if is_prohibition_url:
            logging.info(f'prohibition_url_list--True; deny Scraping; url: {domain};')
            self.result = False
            return self.result
        
        if self.rp.url == '':
            seturl_switch = True
        
        elif urls in self.parse_dict:#urlが評価済み辞書にない場合
            #urlは既にパース済み。
            debug_logger.debug(f'url saved in parse_dict. url: {urls} parse_dict : {self.parse_dict}')
            logging.info(f'url in parse_dict; url: {urls}')
            self.result = self.parse_dict[urls]
            return self.result
        
        elif urls not in self.parse_dict and self.rp.url == robots_url:#urlが評価済み辞書に無く、rp.urlにセットされたrobots.txtへのパス == robots_urlだった場合
            #parse_dictにないがrp.urlとrobots_urlが同じ
            debug_logger.debug('urls not in parse_dict and rp.url is not robots_url')
            debug_logger.debug(f'rp.url | {self.rp.url} | parse_dict: {self.parse_dict}')
            logging.info(f'url is not in parse_dict and rp.url is : True')
            self.result = self.rp.can_fetch(self.useragent, urls)
            self.parse_dict[urls] = self.result
            return self.result
        
        elif urls not in self.parse_dict and self.rp.url != robots_url:#urlが評価済み辞書に無い且つrp.urlにセットされたrobots.txtへのパス != robots_urlだった場合
            seturl_switch = True

        debug_logger.debug(f'seturl_switch: {seturl_switch}')
        if seturl_switch:
            
            session = self.request_check(robots_url)
            #time.sleep(1)#rp.read()を実行する為、一時待機。
            debug_logger.debug(f'session: {session}')
            if session:
                self.result = self.set_url_fetch(urls, robots_url)
                debug_logger.debug(f'self.result: {self.result} ')
        logging.info(f'<robots_url: {robots_url} | urls: {urls} | result: {self.result}>')
        return self.result


