from collections.abc import Iterable
import logging
import numpy as np
from rapidfuzz.distance import Indel
from typing import List
from .texts import ScoringTexts
from mycrawling.logs.debug_log import debug_logger
#Var37.06.14.15a(24/07/25/時点のバージョン)

class ScoringUrls(ScoringTexts):
    ''' urlのスコア算出 '''

    def select_url_scoring_method(self, scoring_type=None):
        ''' urlpathのスコア算出メソッドを指定する。 '''
        if not scoring_type:
            scoring_type = 'all'
        if scoring_type == 'all' or scoring_type == 'max_score_text':
            text_scoring_method = self.urls_text_scoring
        else:
            text_scoring_method = super().best_text_scoring

        return text_scoring_method


    def urls_text_scoring(self,
                         texts,
                         choices,
                         scorer, cutoff=None, *args, **kwargs):
        ''' all_text_scoringの戻り値(generator)を展開して返す '''
        #戻り値はタプル型リストの二次元配列
        score_value = []
        applicable_texts = []
        text_list = []
        text_scores = self.all_text_scoring(texts, choices, scorer, cutoff, *args, **kwargs)
        debug_logger.debug(f'text_scores:{text_scores}')

        #'self.all_text_scoringを呼び出して展開↓↓'
        for score, appl_txt, txt in text_scores:

            score_value.append(score)
            applicable_texts.append(appl_txt)
            text_list.append(txt)

        return score_value, applicable_texts, text_list


    ''' BaseScoringUrls.urls_scoringではscoringメソッドを用いた基本的な
    urlsのスコア付けのみ行う。 '''
    
    def urls_scoring(self, urls_attributes:list,
                     choices_url_text,
                     scoring_method,
                     scorer=None,
                     score_cutoff=None, **kwargs):
        
        ''' ParseUrlsで解析された一つのurlから抽出したpath等の属性値をscoring_methodに基づきスコアリングする '''
        ''' urlの各属性名をスコアリングし、属性毎スコアのリストにした二次元配列を返す。 '''
        #evaluate_textはリスト型を返す。
        ''' 戻り値:リスト型の3次元配列[([],[],[]), ([],[],[])] '''
        if scorer is None:
            scorer = Indel.normalized_distance
        if not callable(scoring_method) and isinstance(scoring_method, str):
            
            scoring_method = self.select_url_scoring_method(scoring_method)
        urls_score = []
        for url in urls_attributes:
            path_split = url.strip('/').split('/')
            debug_logger.debug(f'path_split: {path_split}')
            evaluate_text = scoring_method(
                    texts=path_split,
                    choices=choices_url_text,
                    scorer=scorer,
                    cutoff=score_cutoff,
                    **kwargs
                    )
            
            debug_logger.debug(f'evaluate_text:{evaluate_text}')
            urls_score.append(evaluate_text)
            debug_logger.debug(f'urls_attributes: {urls_attributes} | urls_score: {urls_score}')
            debug_logger.debug(f'any(): {any(urlscore for urlscore in urls_score if urlscore is not None)}')
        return urls_score 


    @classmethod
    def urls_statistics(cls, urls_score:List, statistics):
        ''' urlsのパスを構成するテキストのスコア統計を評価する。'''
        '''
        <staticticsの値>
            'ave': 各スコアの平均スコア
            'median': 各スコアの中央値
            'mode': 各スコアの最頻値
            'rate': 全アイテムに対する閾値を達したスコアの割合※score_cutoffを指定していない場合統計データとしては無効なデータとなる。
            'sum': 各スコアの合計
        '''
        debug_logger.debug(f'urls_score: {urls_score}')
        result = None
        if isinstance(urls_score, (int, float)) or urls_score is None:
            urls_score = [urls_score]
        elif not isinstance(urls_score, Iterable):
            logging.warning(f'無効なデータ型です。urls_score: {urls_score}')
            return result
        
        urls_socre_length = len(urls_score)
        score_list = [s for s in urls_score if s is not None and s != '']
        score_list_length = len(score_list)

        if statistics == 'ave' or statistics == 'average':
            result = np.average(score_list)
        elif statistics == 'median':
            result = np.median(score_list)
        elif statistics == 'rate':
            result = score_list_length/urls_socre_length*100
        elif statistics == 'sum':
            result = np.sum(score_list)
        return result


