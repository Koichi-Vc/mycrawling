from bs4 import BeautifulSoup
from bs4.element import SoupStrainer
from selenium.webdriver import chrome
from selenium.webdriver import edge
from typing import Union
from mycrawling.utils.imports_module import get_module
from mycrawling.logs.debug_log import debug_logger
#Var37.06.14.15a(24/07/25/時点のバージョン)

class ElementsParse:
    ''' htmlの解析 '''      
    defaultparser_name = 'html.parser'
    default_webdriver = None#デフォルトで使用するwebdriverを指定
    
    def __init__(self, webdriver=None, parser_name=None):
        debug_logger.debug(f'parser_name: {parser_name} | self.defaultparser_name: {self.defaultparser_name}')
        if not webdriver:
            webdriver = self.default_webdriver
        webdriver_obj = webdriver if not isinstance(webdriver, str) else get_module(webdriver)
        self.webdriver = webdriver_obj
        self.htmlparser = parser_name if parser_name else self.defaultparser_name


    def element_strainer(self, parse_only_tag:Union[str, None] = None):
        ''' パース対象タグを指定する '''
        parse_tag = parse_only_tag

        if not isinstance(parse_tag, SoupStrainer):
            parse_tag = SoupStrainer(parse_tag)
        return parse_tag

    
    def element_parse(self, data , parser=None,  parse_only_tag=None):
        ''' dataをbs4.elementオブジェクトに変換する '''
        if not parser:
            parser = self.htmlparser
        
        #print(f'element_parse>>> parser: {parser} | parse_only_tag: {parse_only_tag}\n')
        parse_tag = self.element_strainer(parse_only_tag=parse_only_tag)
        
        if isinstance(data, self.webdriver):
            soup = BeautifulSoup(data.page_source, features=parser, parse_only=parse_tag)

        elif isinstance(data, str):
            soup = BeautifulSoup(data, features=parser, parse_only= parse_tag)
        elif isinstance(data, BeautifulSoup):
            soup = data
        return soup

