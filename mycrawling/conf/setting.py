from pathlib import Path

package_root = Path(__file__).parent.parent.parent

'''
USE_CLASSES:
    使用するクラスのインポートパスを指定する。

REGISTRY_DATA_CLASS_INSTANCE:
    データクラスをインスタンス化した上で登録する。

PARAMETERHANDLER:
    パラメータ管理クラスを指定する。    
'''

USE_WEBDRIVER = 'selenium.webdriver.Chrome'

WEBDRIVER_MANAGER = 'mycrawling.webdriver_manages.webdriver_manager.chromedriver_manager.ChromeWebDriverContextManager'

#webdrivermanagerクラスに渡すパラメータ値
'''
timeout:
    webdriver起動時のタイムアウトを指定する。
    ※尚robots.txtの所在確認をするためのrequest_checkのタイムアウトは、ROBOTFILEPARSE_PARAMETERのrequest_check_timeoutに指定する。
'''
WEBDRIVER_MANAGER_PARAM = {
    'timeout': 20,
}

#webdriverのServiceクラスへ渡すパラメータ値
WEBDRIVER_SERVICE_PARAM = {}

CRAWLING_CLASS = 'mycrawling.crawlings.crawling.MyCrawlingSearch'

CRAWL_DELAY_TIME = 7

#25/2/14/536am;次回以降ロボット解析オブジェクトのインポート先について考える。
#robots.txtの解析を行うオブジェクト
ROBOTMANAGER = 'mycrawling.robots.robotfileparse.RobotFileparseManager'


#REGISTRY_CLASSの後継。変数名が適切ではないと思ったのとより、改善をめざした。
USE_CLASSES = {
    'robotfileparse': 'mycrawling.robots.robotfileparse.RobotFileparseManager',
    'searchanchorelements': 'mycrawling.searchelements.anchor_elements.elements.SearchAnchorElements',
    'evaluateanchorelements': 'mycrawling.searchelements.anchor_elements.evaluation.EvaluateAnchorElements',
    'pagescorings':  'mycrawling.pageanalyser.pagescorings.PageScorings',
    'evaluaterobotsmeta': 'mycrawling.searchelements.metaelements.attrs_robot.EvalRobotsMetaElements',
    'scraping': 'mycrawling.scrapings.scraping.PageScraping'
}


#インスタンス化するタイミングを遅延させるクラス。
LAZY_INSTANCES_CLASS = {
    'pageevaluation': 'mycrawling.pageanalyser.pageevaluations.PageEvaluation',
}

#a要素検索用の設定情報

#データクラスインスタンス

REGISTRY_DATA_CLASS_INSTANCE = {
    'robotsparsedatalist': 'mycrawling.robots.data.prohibitions.RobotsParseDataList',
    'reference_title_a_url_texts':'mycrawling.datas.referencetexts.Reference_Title_A_Url_Texts',
    'reference_textcollection': 'mycrawling.datas.referencetexts.Reference_TextCollection',
}


''' CREATEFILTER_CLSのキーに関して、現状は、クラス名を使っているが、一度要素(タグ)名で指定してみる。 '''
#フィルターを作成するクラス
CREATEFILTER_CLS = {
    'a': 'mycrawling.filters.anchorelements.CreateAnchorElementFilter',
}


#複数のフィルターを組み合わせるフィルターセットを作成するクラス
CREATEFILTERSETS_CLS = 'mycrawling.filters.filtersets.Elements_Filterset'


#要素検索のフィルターを管理するクラスを指定※廃止。
#FILTER_PARAMETER_HANDLER = 'mycrawling.filters.parameter.ElementsFilterParameterHandler'

FILTER_PARAMETER_FILE = package_root.joinpath('mycrawling/parameter_files/elements_filter_arguments.json')

#mediatorの指定。
USE_MEDIATOR_PATH = 'mycrawling.conf.data_setting.datamediator'

#リファレンステキスト
REFERENCE_TEXTS_FILES = package_root.joinpath('mycrawling/parameter_files/ref_textfiles/ref_texts.json')

#ページ評価(pageevaluation)クラスのインスタンス化用パラメータ
PAGEEVALUATION_PARAMETER = {
    'datamediator': USE_MEDIATOR_PATH
}

#mycrawlingでクローリング時に使用するクラスのインスタンス化用パラメータ
'''
USE_CLASSES_PARAMETER = {
    'robotfileparse': {
        'datamediator': USE_MEDIATOR_PATH,
        
    }
}'''

USE_CLASSES_PARAMETER = package_root.joinpath('mycrawling/parameter_files/create_instance_parameters.json')

ROBOTS_ERROR_MESSAGE_DICT = {
    'requests.exceptions.Timeout': {
        'textmessage': 'タイムアウトです。robots.txtが参照出来ませんでした。',
        'logmessage':'None robots.txt or TimeOut. robots.txtの参照失敗 ',
        'loglevel': 'error'
        },

    'requests.exceptions.RequestException': {
        'textmessage': ('robotsファイルへのリクエストに問題が発生しました。'),
        'logmessage': f'robotsファイルリクエスト/取得に問題発生'
        },

    ValueError: {
        'textmessage': 'robotsファイル取得に問題が発生しました。',
        'logmessage': f'robots.txt参照エラー',
        'loglevel':'error'
        }
}


#robots.txtを解析するクラス(robotfileparse)のインスタンス化用パラメータ
ROBOTFILEPARSE_PARAMETER = {
    'rp': 'urllib.robotparser.RobotFileParser',
    'request_check_timeout': 10,
    'useragent': '*',
    'datamediator': USE_MEDIATOR_PATH,
    'error_loghandling_obj': 'mycrawling.logs.errors.Errorloghandlings_Class',
    "notify_to_attr": "get_time_sleep" 
}

ROBOTPARSER_PARAMETER = None

SCRAPINGS_CLASS_PARAMETER = None

ROBOTS_SETUP_LOGGER = {
    'getlogger': 'robots_error_log',
    'handler': 'logging.StreamHandler',
    'formatter': '%(asctime)s | %(created)s | %(name)s | %(levelname)s | robots_url: %(robots_url)s | %(message)s | '
}

#エラーハンドリングクラスのパラメータ
ROBOTS_ERRORLOGHANDLING_PARAMETERS = {
    'logger': 'robots_error_log',
    'catch_exception': False,
    'logger_conf_variable': ROBOTS_SETUP_LOGGER,
    'custom_message_dict': 'ROBOTS_ERROR_MESSAGE_DICT'
}

Debug = False


