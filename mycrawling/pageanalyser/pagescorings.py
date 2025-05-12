from bs4 import element as bs4_element
import logging
from rapidfuzz.fuzz import WRatio as rapd_WRatio
from rapidfuzz.distance import Indel
from types import GeneratorType
from typing import Iterable
from .data import PageScoreStatisticsSet
from .pageparse import PageTextContentsParse
from mycrawling.scorings.texts import ScoringTexts
from mycrawling.scorings.texts import ScoringTitleTexts
from mycrawling.evaluations.evaluationtexts import EvaluateTexts
from mycrawling.utils.imports_module import get_module
from mycrawling.logs.debug_log import debug_logger

#Var37.06.14.15a(24/07/25/時点のバージョン)
class PageScorings(PageTextContentsParse, ScoringTexts):
    
    default_text_scorer = Indel.normalized_distance

    def __init__(self, reference_object:'Reference_TextCollection'=None, reference_title_a_url_texts:'Reference_Title_A_Url_Texts'=None, title_boundary = None, text_boundary=None, **kwargs):

        datamediator = kwargs.get('datamediator', None)
        if datamediator and isinstance(datamediator, str):
            datamediator = get_module(datamediator)

        if reference_object:
            self.reference_object = reference_object
        elif datamediator:
            self.reference_object = datamediator.get_instance('reference_textcollection')
        else:
            raise TypeError('PageScorings() に必要な引数"reference_object"が足りません。')

        if reference_title_a_url_texts:
            self.reference_title_a_url_texts = reference_title_a_url_texts
        elif datamediator:
            self.reference_title_a_url_texts = datamediator.get_instance('reference_title_a_url_texts')
        else:
            raise TypeError('PageScorings() に必要な引数"reference_title_a_url_texts"が足りません。')
        debug_logger.debug(f'reference_object: {self.reference_object}')
        debug_logger.debug(f'reference_object.all_reference_text_list: {hasattr(self.reference_object, "all_reference_text_list")}| get_all_fields: {hasattr(self.reference_object, "get_all_fields")}')
        
        try:
            reference_attrs = self.reference_object.get_all_fields()

        except TypeError:
            logging.warning('データクラスインスタンスに属性が見つかりません')
            reference_attrs = {}

        debug_logger.debug(f'reference_attrs: {reference_attrs}')
        for attr in reference_attrs:
            setattr(self, attr, reference_attrs[attr])
        
        self.company_about = kwargs.pop('company_about', self.reference_title_a_url_texts.reference_texts)
        self.do_parsetext = kwargs.pop('do_parsetext', True)
        exclude_ref_words = kwargs.pop('exclude_ref_words', set())

        if isinstance(exclude_ref_words, str) and 'self.' in exclude_ref_words:
            #自クラス内のメンバーを指定した場合は取得する。
            exclude_ref_words = exclude_ref_words.removeprefix('self.')
            exclude_ref_words = getattr(self, exclude_ref_words, set())
        elif isinstance(exclude_ref_words, str) and '.' in exclude_ref_words:
            #ドットが含まれる場合はインポートパスと解釈する。
            #ドットをただの文字列として認識させる場合は、set型で渡すこと。
            exclude_ref_words = get_module(exclude_ref_words)
        elif isinstance(exclude_ref_words, str):
            #語彙を直接指定した場合はsetにして保持。
            exclude_ref_words = {exclude_ref_words}

        debug_logger.debug(f'exclude_ref_words: {exclude_ref_words}')
        self.exclude_ref_words = exclude_ref_words

        self.title_scorer = rapd_WRatio
        self.title_boundary = title_boundary if title_boundary else 80
        self.scoring_title_texts = ScoringTitleTexts(ref_title_choices=[self.company_about, self.all_reference_text_list])#使うか現段階では不明。
        
        self.text_scorer =  kwargs.pop('text_scorer', self.default_text_scorer)
        self.scoring_eval = EvaluateTexts()
        self.text_boundary = text_boundary if isinstance(text_boundary, (int, float)) else 0.3
        self.reqd_child_count = 4        
        self.high_score_jp_text = list()#言語別の検出語彙※現状未使用
        self.high_score_en_text = list()#言語別の検出語彙※現状未使用
        self.primary_text_list = list()#ページ内から検出した重要語彙
        self.high_score_text_list = list()#ページ内から検出した高類似度語彙


    @property
    def text_scorer(self):
        return self.__text_scorer
    
    @text_scorer.setter
    def text_scorer(self, algorithm):
        self.__text_scorer = algorithm

    
    @property
    def primary_text_list(self):
        return self.__primary_text_list

    @primary_text_list.setter
    def primary_text_list(self, values):

        if not hasattr(self, 'primary_text_list'):
            self.__primary_text_list = list()

        if isinstance(values, str):
            if values not in self.__primary_text_list:
                self.__primary_text_list.append(values)
            
        elif isinstance(values, Iterable):        
            for value in values:
                if value not in self.__primary_text_list:
                    self.__primary_text_list.append(value)

    @property
    def high_score_text_list(self):
        return self.__high_score_text_list
    
    @high_score_text_list.setter
    def high_score_text_list(self, values):
                
        if not hasattr(self, 'high_score_text_list'):
            self.__high_score_text_list = list()
        
        if isinstance(values, str):
            if values not in self.__high_score_text_list:
                self.__high_score_text_list.append(values)

        elif isinstance(values, Iterable):
            for value in values:
                if value not in self.__high_score_text_list:
                    self.__high_score_text_list.append(value)


    #PageEvaluation.high_score_search_betaと同じ
    def detect_high_score_texts(self, element, scorer=None, **kwargs):
        ''' PageEvaluationからhigh_score_search_betaの機能を一部分離した。 '''
        text_scorer = scorer if callable(scorer) else self.text_scorer

        if not isinstance(element, bs4_element.Tag):
            return
        #25/03/26/0501am; ここだけ新規で追加。うまく行かなかったら即削除。※ここ１
        #elements_texts = [ i.strip() for i in element.text.strip().split('\n' or '\t') if i.strip() != '']
        
        #debug_logger.debug(f'elements_texts: {elements_texts}')

        text_contents = self.run_parse_textcontents(element, do_parsetext=self.do_parsetext, exclude_ref_words = self.exclude_ref_words, **kwargs)
        text_contents = [txt for txt in text_contents]
        debug_logger.debug(f'text_contents: {text_contents}')
        evaluated_text = self.all_text_scoring(
            text_contents,
            choices=self.all_reference_text_list,
            text_scorer=text_scorer,
            cutoff= self.text_boundary
            )#contents_parser⇒self        
        
        for score, ext_txt, txt in evaluated_text:
            debug_logger.debug(f'score: {score} | txt: {txt} | ext_txt: {ext_txt}')
            if score is not None:

                if ext_txt in self.all_primary_texts:
                    self.primary_text_list = txt
                else:
                    self.high_score_text_list = txt
                ''' 全ての高類似度テキストを言語別に格納'''
                if ext_txt in self.jp_standard_texts:
                    self.high_score_jp_text.append(txt)
                elif ext_txt in self.en_standard_texts:
                    self.high_score_en_text.append(txt)

        return self.primary_text_list, self.high_score_text_list


    #child_elements_parseと同じで後継を想定したクラス。
    def child_elements_traverse_beta(self, element):
        ''' 各要素の子要素を走査し、ルート要素から抽出した全ての高類似度語彙の含有量を調べる '''
        ''' 
        変数解説
            detect_text_is_true:
                子要素から対象のテキストが検出された時にTrueに更新し、child_countのインデックス2(重要語彙・高類似度スコアを検出した子要素)を加算する。

            texts_similarity:
                子要素のテキストを語彙別にスコアリングした結果をジェネレータ型で保持する。
                
        '''

        child_length = 0#要素に属する直接の子要素総数
        child_count = 0#子要素の内テキストが検出された要素の数

        detection_highscore_count = 0#子要素内から検出された高類似度語彙の数
        detection_primary_count = 0#子要素内から検出された重要語彙の数
        
        detection_primary_text = set()#検出した重要語彙の種類; 24/06/10/323am
        detection_highscore_text = set()#検出した高類似度テキストの種類; 24/06/10/323am

        contain_text = set()#childrenの走査で既に出現した高類似度・重要テキストを保持する。
        children = element.children
        child_length = len([
            c for c in element.contents if isinstance(c, bs4_element.Tag) or (isinstance(c, str) and c.strip() != '')])
        
        if not child_length or child_length < self.reqd_child_count:
            #子要素総数が評価条件に必要な子要素数を満たしているか評価する。
            return None
        debug_logger.debug(f'child_lengthの数: {child_length}')
        
        children_list = self.run_parse_textcontents_list(children)

        for child in children_list:
            debug_logger.debug(f'child: {child}')
            #childがジェネレータ式ならば展開してtextsに保持、リスト型ならそのまま。
            if isinstance(child, GeneratorType):
                texts = [txt for txt in child]
            else:    
                texts = child

            if texts:
                detect_text_is_true = False
                texts_similarity = self.all_text_scoring(texts, choices=self.all_reference_text_list, cutoff= 0.45)
                match_primary_texts = self.scoring_eval.collect_contain_texts(texts, reference_texts=self.primary_text_list)
                match_high_score_texts = self.scoring_eval.collect_contain_texts(texts, reference_texts=self.high_score_text_list)
                debug_logger.debug(f'match_primary_texts: {match_primary_texts}')
                debug_logger.debug(f'match_high_score_texts: {match_high_score_texts}')
                debug_logger.debug('start texts_similarity>>>')
                for similarity_score in texts_similarity:
                    is_primary_texts = False
                    is_high_score_texts = False
                    text = similarity_score[2]
                    similarity = similarity_score[0]
                    debug_logger.debug(f'text: {text} | similarity: {similarity}')

                    if text in match_primary_texts and similarity is not None:
                        is_primary_texts = True
                        detection_primary_count += 1
                        detection_primary_text.add(text)
                        if text not in self.primary_text_list:
                            self.primary_text_list.append(text)
                    
                    elif text in match_high_score_texts and similarity is not None:
                        is_high_score_texts = True
                        detection_highscore_count += 1
                        detection_highscore_text.add(text)
                        if text not in self.high_score_text_list:
                            self.high_score_text_list.append(text)

                    if detect_text_is_true is False and (is_primary_texts or is_high_score_texts):
                        detect_text_is_true = True
                
                debug_logger.debug(f'text roop end>>>')
                debug_logger.debug(f'is_primary_texts:{is_primary_texts} | is_high_score_texts: {is_high_score_texts}')                                                  
                if detect_text_is_true:
                    child_count += 1

        debug_logger.debug(f'contain_text: {contain_text}')
        debug_logger.debug(f'{child_count} | {detection_highscore_count} | {detection_primary_count} |')    
        return PageScoreStatisticsSet.create_dataclass(child_length,
                                                       child_count,
                                                       detection_highscore_count,
                                                       detection_highscore_text,
                                                       detection_primary_count,
                                                       detection_primary_text)


    def scoring_titles(self, soup_obj):
        ''' ページのtitle要素の検索と類似度スコアリング、評価 '''
        titles = soup_obj.find_all('title')
        title_score = None
        is_contain = None

        if titles:
            is_contain = any(self.reference_title_a_url_texts.texts_is_contain(title.text.strip()) for title in titles)
            title_scorer = self.title_scorer
            choices_list = [self.company_about, self.all_reference_text_list]
            for choices in choices_list:
                self.scoring_title_texts.ref_title_choices = choices
                title_score, title_text = self.scoring_title_texts.scoring_title_elements(titles,
                                                                      cutoff= self.title_boundary,
                                                                      text_scorer=title_scorer)#obj_parser⇒self
                if title_score:
                    break
        else:
            title_score = None

        return title_score,title_text, is_contain


