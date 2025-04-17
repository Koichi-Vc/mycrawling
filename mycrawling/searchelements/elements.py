import bs4
from typing import Dict
from mycrawling.parse.elementsparse import ElementsParse
from mycrawling.logs.debug_log import debug_logger


#Var37.06.14.15a(24/07/25/時点のバージョン)
class BaseSearchElements(ElementsParse):
    
    defaultparser_name = 'lxml'

    def __init__(self, tag=True, attrs_value:Dict=None, string=None, webdriver=None, parser_name=None, **query_kwargs):
        '''
        !留意点!:
            Beautifulsoup.find_allの仕様として第二引数に位置引数を渡した場合、内部的にclass属性に対するフィルターと解釈される。

        args:
            tag: 
                検索するタグ。BeautifulSoup.find_allのname引数に渡される。
            attrs_value:
                属性名-属性値(又はフィルターメソッド)の辞書

            query_kwargs: 
                find_allが受け取る引数をまとめて指定
                !同じキーがattr_nameに存在していた場合attr_name側キーが優先される。
        '''
        print('BaseSearchElements>>>>>>')
        print(f'query_kwargs: {query_kwargs}')
        
        if 'name' in query_kwargs:
            #キーワード引数としてnameは指定出来ない。
            del query_kwargs['name']
        tagname = tag
        self.tag = tagname#タグの条件
        self.attrs_value = {}#属性名を始めとした検索フィルター条件
        self.string = string#テキストを対象とした検索フィルター条件
        self.query_kwargs = query_kwargs#その他条件指定。

        if attrs_value and isinstance(attrs_value, dict):
            self.attrs_value.update(attrs_value)#キーワード(属性名)によるフィルターを保持

        #attrs_valueで指定したキーがquery_kawrgsで確認された場合query_kwargs側のキーを削除する。
        for attr_name in self.attrs_value:
            if attr_name in self.query_kwargs:
                del self.query_kwargs[attr_name]

        super().__init__(webdriver=webdriver, parser_name=parser_name)


    def __call__(self, soup_obj, **kwargs):
        debug_logger.debug(f'tag:{self.tag} | attrs: {self.attrs_value} | query: {self.query_kwargs}')        
        soup_obj = self.element_parse(soup_obj, **kwargs)#BeautifulSoupオブジェクトを解析する。

        elements = (
            elem for elem in soup_obj.find_all(self.tag, self.attrs_value, string=self.string, **self.query_kwargs))
        return elements



    #内容は__call__メソッドと同じ.
    def find_elements(self, soup_obj:bs4.BeautifulSoup):
        #処理は__call__と同じであるが、soup_objはbs4.BeautifulSoupのみを受け取る。
        debug_logger.debug(f'tag:{self.tag} | attrs: {self.attrs_value} | query: {self.query_kwargs}')        

        elements = (
            elem for elem in soup_obj.find_all(self.tag, self.attrs_value, string=self.string, **self.query_kwargs))
        return elements


