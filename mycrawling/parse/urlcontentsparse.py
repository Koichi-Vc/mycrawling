from urllib.parse import urlparse
from typing import List


#Var37.06.14.15a(24/07/25/時点のバージョン)

class ParseUrls():
    ''' urlの具体的な属性名解析 '''

    def parse_urls(self, urls:List, *urlattrs):
        ''' urlsの解析結果を{url名: {attr:value}} の辞書形式で返す '''
        urls_attrvalue_dict = {}
        if isinstance(urls, str):
            urls = [urls]
        elif isinstance(urls, (int, float)):
            return urls_attrvalue_dict
        
        for url in urls:
            #url = urls.pop()
            parsed_url = urlparse(url)
            result = {}#属性名をキーにしてvalueを格納
            
            for attr in urlattrs:
                attr_value = getattr(parsed_url, attr, None)
                result[attr] = attr_value
            urls_attrvalue_dict[url] = result
        
        return urls_attrvalue_dict


    def hostname_parse(self, *urls_list):
        ''' urlリストからホストネームを抽出する。 '''
        hostname_dict = None
        hostname = ['hostname']
        urls_hostname = self.parse_urls(urls_list, *hostname)
        #各ホストネームをurls_listのurlアイテムをキーとして辞書型で格納する。
        if urls_hostname:
            hostname_dict = {url:urls_hostname[url]['hostname'] for url in urls_hostname}
        return hostname_dict    


    def get_one_url_attrs(self, url, *urlsattrs):
        ''' 一つのurlを解析し各属性値を返す。 '''
        attrs_list = []
        url_attrs_result = self.parse_urls([url], *urlsattrs)
        if url_attrs_result:
            attrs_value = url_attrs_result[url]#urlの属性を参照
            attrs_list = [attrs_value[attrs] for attrs in attrs_value]#属性値のみを取り出す
        return attrs_list


