from typing import List
from collections import deque
from bs4.element import Tag
import re
from rapidfuzz import process as rpdfuzz_process
from rapidfuzz.fuzz import WRatio as rapidfuzz_WRatio
from rapidfuzz.distance import Indel
from mycrawling.parse.textcontentsparse import Spacy_TextParse
from mycrawling.logs.debug_log import debug_logger

#Var37.06.14.15a(24/07/25/時点のバージョン)

class ScoringTexts:
    """ テキストのscoringを実行する。 """
    """ 
    all_text_scoringとbest_text_scoringの違いは、テキストコンテンツリストのスコアリング時に
    all_text_scoring全てのスコアを返し、best_text_scoringはリスト中の最高スコアのみを返す。
    """
    default_all_text_scorer = Indel.normalized_distance
    default_best_text_scorer = Indel.normalized_distance
    #base_text_scoringだったが存在意義が薄れた為、ひとまずジェネレータ化するメソッドとして対応する。
    def decorator_text_scoring(parse_method):
        def wrapper(self, texts, choices, scorer, *args, **kwargs):
            query_txt = ''
            ext_txt = ''
            #debug_logger.debug(f'base_text_scoring>>> args: {args} | kwargs: {kwargs}')
            #debug_logger.debug(f'score_init確認: {self.__score_cutoff_init_}')
            if isinstance(texts, str):
                ''' list型以外が渡されたら変換 '''
                texts = [texts]
            #ジェネレータ型(parsed_texts)を展開する。
            for score, ext_txt, query_txt in parse_method(self, texts, choices, scorer, *args, **kwargs):
                yield score, ext_txt, query_txt  
        return wrapper


    def all_text_scoring(self,
                         texts,
                         choices,
                         text_scorer=None, cutoff=None ,*args, **kwargs:dict['custom_initvalue': '']):
        ''' テキストリスト内全アイテムのスコアを順次返す。cutoff値外又は評価不能の場合はNoneを返す。'''

        debug_logger.debug(f'self has text_scorer: {hasattr(self, "text_scorer")}')

        if not text_scorer and hasattr(self, 'text_scorer'):
            text_scorer = self.text_scorer
        elif not text_scorer or not callable(text_scorer):
            text_scorer = self.default_all_text_scorer

        if isinstance(texts, str):
            ''' list型以外が渡されたら変換 '''
            texts = [texts]

        applicable_txt = None
        score = None
        default = kwargs.pop('default', None)#デフォルトのスコア値

        for txt in texts:
            if txt is None:
                txt = ''
            debug_logger.debug(f'txt: {txt}')
            re_txt = re.sub(' |　', '', txt)
            re_txt = re_txt.casefold()
            score_value = rpdfuzz_process.extractOne(re_txt, choices=choices, score_cutoff=cutoff, scorer=text_scorer)
            if score_value is not None:
                score = score_value[1]
                applicable_txt = score_value[0]#choicecリスト内の該当テキスト
            else:
                score = default#score_valueがNoneの場合デフォルト値を代入
                applicable_txt = ''
            yield score, applicable_txt, txt


    def best_text_scoring(self, texts:List, choices, text_scorer=None, cutoff=None ,*args, **kwargs):
        ''' テキストリストの最高スコアを返す。cutoff値外又は評価不能の場合はNoneを返す。 '''
        
        if isinstance(texts, str):
            ''' list型以外が渡されたら変換 '''
            texts = [texts]
            
        if not text_scorer and hasattr(self, 'text_scorer'):
            text_scorer = self.text_scorer
        elif not text_scorer or not callable(text_scorer):
            text_scorer = self.default_best_text_scorer
        
        applicable_txt = None
        text_item = None
        score = None

        for txt in texts:
            if txt is None:
                txt = ''
            txt = re.sub(' |　', '', txt)
            txt = txt.casefold()
            score_value = rpdfuzz_process.extractOne(txt, choices=choices, score_cutoff=cutoff, scorer=text_scorer)

            if score_value:
                score = score_value[1]
                cutoff = score
                applicable_txt = score_value[0]
                text_item = txt
        debug_logger.debug(f'score: {score} | text_item: {text_item}')
        return score, applicable_txt, text_item


#Var37.06.14.15a(24/07/25/時点のバージョン)
class ScoringTitleTexts(ScoringTexts):
    ''' title要素のスコア算出 '''
    title_scorer = rapidfuzz_WRatio
    text_parser = Spacy_TextParse

    def __init__(self, ref_title_choices:List=None):
        
        if not ref_title_choices:
            ref_title_choices = list()

        elif not isinstance(ref_title_choices, (list, tuple, deque)):
            ref_title_choices = [ref_title_choices]

        self.ref_title_choices = ref_title_choices

    @property
    def ref_title_choices(self):
        return self._ref_title_choices
    
    @ref_title_choices.setter
    def ref_title_choices(self, ref_texts:List):
        self._ref_title_choices = ref_texts
    

    def scoring_title_elements(self, titles:List[Tag], cutoff=80, text_scorer=None, ):
        choices = self.ref_title_choices

        debug_logger.debug(f'choices: {choices} | cutoff: {cutoff}')
        text_scorer = text_scorer if callable(text_scorer) else self.title_scorer
        title_score = None
        text = None
        if isinstance(titles, str):
            titles = [titles]
        if isinstance(choices, str):
            choices = [choices]
        
        title_text = (tt.text.strip() for tt in titles)
        scoring_title = self.best_text_scoring(texts=title_text,
                                               choices=choices,
                                               text_scorer=text_scorer,
                                               cutoff=cutoff)
        scored_title = scoring_title[0]
        
        debug_logger.debug(f'scoring_title: {scoring_title} | scored_title: {scored_title}')
        if scored_title is not None:
            title_score = scored_title
            text = scoring_title[2]

        debug_logger.debug(f'score:{title_score} | text: {text}')
        return title_score, text

