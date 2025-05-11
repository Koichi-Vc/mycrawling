from typing import Union, List
from .base import ScoreEvaluations
from mycrawling.utils.operators import SelectListOperator
from mycrawling.scorings.texts import ScoringTexts
from mycrawling.logs.debug_log import debug_logger


#Var37.06.14.15a(24/07/25/時点のバージョン)
class EvaluateTexts(ScoreEvaluations, SelectListOperator):
    ''' 文字列の評価 '''
    
    scoring_texts = ScoringTexts()


    def texts_is_contain(self, texts:Union[List, str], reference, **kwargs):
        ''' テキストと参照テキスト(reference)との完全一致、部分一致をbool型で評価する '''
        
        debug_logger.debug(f'texts: {texts} | reference: {reference}')
        if isinstance(texts, str):
            texts = [texts]
        
        for txt in texts:
            result = False
            remove_whitespace = txt.replace(' ', '')#空白スペースを消したタイプも検証する。
            remove_full_width_space = txt.replace('　', '')#
            #debug_logger.debug(f'texts_is_contain>>txt:{txt}')
            for ref in reference:

                if (txt in ref or ref in txt) or (remove_whitespace in ref) or (remove_full_width_space in ref):
                    result = True
                    break
            yield txt, result


    def collect_contain_texts(self, texts, reference_texts, **kwargs):
        ''' テキストコンテンツと参照テキスト其々含まれている部分を評価し、該当するテキストを返す '''
        
        contain_texts = set()
        if not reference_texts:
            reference_texts = getattr(self, 'reference_texts', set())
            
        contain_results = self.texts_is_contain(texts, reference_texts)

        for results in contain_results:
            #debug_logger.debug(f'results: {results}')
            text = results[0]
            is_contain = results[1]
            if is_contain:
                contain_texts.add(text)
        
        debug_logger.debug(f'contain_texts:{contain_texts}')
        return contain_texts


