import logging
from typing import List
from bs4.element import Tag
from collections.abc import Iterable
from mycrawling.parse.textcontentsparse import Spacy_TextParse

#Var37.06.14.15a(24/07/25/時点のバージョン)

class PageTextContentsParse(Spacy_TextParse):
    ''' 訪問したサイトページのテキストコンテンツを解析し、分かち書きする。 '''
    
    default_exclude_ref_words = set()

    def run_parse_textcontents(self, elements:Tag, do_parsetext=True, **kwargs):
        ''' 解析したhtml要素からテキストコンテンツを返す。'''
        '''
        args:
            do_parsetext: 要素から抽出したテキスト自体を解析し分かち書きする場合はTrue
            exclude_ref_words: 解析対象から除外する語彙を指定する。
        '''

        exclude_ref_words = kwargs.pop('exclude_ref_words', self.default_exclude_ref_words)
        texts = list()
        if isinstance(elements, Tag) and not hasattr(elements, 'text'):
            logging.warning('テキストを抽出できません')
            return
        elif isinstance(elements, Tag):
            texts = (i.strip() for i in elements.text.strip().split('\n' or '\t') if i.strip() != '')
        elif isinstance(elements, str):
            texts = [texts]
        elif isinstance(elements, Iterable):
            texts = elements
        

        if do_parsetext and not exclude_ref_words:
            parsed_text = (ps_txt for txt in texts for ps_txt in self.textparse(txt))
            return (text for text in parsed_text)
        

        elif do_parsetext and exclude_ref_words:
            parsed_text = list()
            for txt in texts:
                if txt in exclude_ref_words:
                    parsed_text.append(txt)
                else:
                    parse = self.textparse(txt)
                    parsed_text += parse
            return (text for text in parsed_text)
        
        else:
            return texts


    def run_parse_textcontents_list(self, elements:List, do_parsetext=True):
        ''' 複数の要素を順次解析したhtml要素からテキストコンテンツをジェネレータ式で返す。'''
        
        for element in elements:
            if not hasattr(element, 'text'):
                logging.warning('テキストを抽出できません')
                return
            
            texts = (i.strip().replace(' ','') for i in element.text.strip().split('\n' or '\t') if i.strip() != '')
            if do_parsetext:
                parsed_text = (ps_txt for txt in texts for ps_txt in self.textparse(txt))
                yield [text for text in parsed_text]
            
            else:
                yield texts


