import logging
import re
from spacy import load as spacy_load
from spacy.tokens.doc import Doc as spacy_DoC_Type
from mycrawling.logs.debug_log import debug_logger

#Var37.06.14.15a(24/07/25/時点のバージョン)

class Spacy_TextParse:
    ''' テキストを解析する。 '''

    jp_models = 'ja_ginza'
    en_models = 'en_core_web_sm'
    japaniexe_parser = spacy_load(jp_models)#MeCabを解析に用いる
    english_parser = spacy_load(en_models)


    @classmethod
    def is_jp_language(cls, texts):
        #日本語のテキストが含まれているか評価する。       
        is_contain_jp = bool(re.search(r'[ぁ-んァ-ヶｱ-ﾝﾞﾟ一-龠]+', texts))
        return is_contain_jp


    @classmethod
    def textparse(cls, texts, *getattr_name, **kwargs):
        ''' テキストを解析する '''
        #print('Spacy_TextParse.textparse>>>\n')
        #print(f'texts: {texts}')
        listing = kwargs.pop('listing', True)

        if not isinstance(texts, str):
            logging.warning(f'テキスト、文字列を渡してください | texts: {texts}')
            return
        
        if 'text' not in getattr_name:
            getattr_names = [attr for attr in getattr_name]
            getattr_names.insert(0, 'text')
        else:
            getattr_names = getattr_name
            
        is_jp_language = cls.is_jp_language(texts)#日本語のテキストか調べる。
        #print(f'language: {language}')

        parser = cls.japaniexe_parser

        if is_jp_language is False:
            parser = cls.english_parser
     
        parsed_text = parser(texts)

        if listing is True:
            parsed_text = cls.listing_parsed_text(parsed_text, *getattr_names)
        #print('Spacy_TextParse.textparse>>>\n')
        return parsed_text
    

    @classmethod
    def listing_parsed_text(cls, parsed_text, *get_attrname):
        ''' 解析後のテキストを必要に応じてリスト化する。 '''
        ''' !注意: MeCab用に最適化されている為、他パーサーの場合の動作は非サポートです。 '''
        #戻り値: リスト型の二次元配列で内側リストのアイテム数は8
        
        parsed_text_list = []
        if not isinstance(parsed_text, spacy_DoC_Type):
            return

        
        for parsed_text in parsed_text:
            parsed_item = []
            for attr in get_attrname:

                attr_name = getattr(parsed_text, attr, '')
                parsed_item.append(attr_name)
            parsed_text_list.append(parsed_item)

        is_single = all(len(item)==1 for item in parsed_text_list)
        debug_logger.debug(f'parsed_text_list: {parsed_text_list}')
        #次元毎に持つアイテム数が単一の場合次元を1次元に減らす
        if is_single:
            parsed_text_list = [item[0] for item in parsed_text_list]
        return parsed_text_list


