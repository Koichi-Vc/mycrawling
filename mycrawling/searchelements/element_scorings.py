from rapidfuzz.distance import Indel
from typing import Union, List, Tuple, Set
from mycrawling.scorings.texts import ScoringTexts
from mycrawling.logs.debug_log import debug_logger


#Var37.06.14.15a(24/07/25/時点のバージョン)
class ElementsScoring(ScoringTexts):
    ''' 要素のテキストコンテンツをスコアリング '''
    def __init__(self, ref_text:Union[List, Tuple, Set]=None, **kwargs):
        self.reference_texts = ref_text
        self.text_scorer = Indel.normalized_distance
        self.text_score_cutoff = kwargs.pop('text_score_cutoff', 0.3)
        #self.datamediator = kwargs.pop('datamediator', None)


    @property
    def text_scorer(self):
        ''' scoringのアルゴリズムを参照 '''
        return self.__text_scorer
    
    @text_scorer.setter
    def text_scorer(self, scorer):
        self.__text_scorer = scorer 
    
    @property
    def reference_texts(self):
        return self.__reference_texts

    @reference_texts.setter
    def reference_texts(self, texts):
        self.__reference_texts = texts
    
    def all_textcontent_scoring(self, texts, choices, scorer, cutoff, return_score_only=True, *args, **kwargs):
        """ 要素のテキストアイテムを順次スコアリングして返す。"""
        """
        return_score_only:
             スコア値のみを返す場合はTrue, (score, applicable_txt, txt)で返す場合はFalse
        """

        #スコアのみを返す場合はreturn_score_onlyをTrue
        #戻り値はリスト型又はタプル型リストの二次元配列
        #戻り値データ型はリストの二次元配列
        choices = self.__reference_texts
        scorer = self.text_scorer
        cutoff = self.text_score_cutoff

        text_scores = self.all_text_scoring(texts,
                                            choices,
                                            scorer,
                                            cutoff, *args, **kwargs)
        #a要素リスト全てのテキストコンテンツをスコアリングしリストにまとめる。
        debug_logger.debug(f'text_scores: {text_scores}')
        return text_scores
  

    def best_textcontent_scoring(self, texts, *args, **kwargs):
        choices = self.__reference_texts
        scorer = self.text_scorer
        cutoff = self.text_score_cutoff

        return self.best_text_scoring(texts, choices, scorer, cutoff, *args, **kwargs)


