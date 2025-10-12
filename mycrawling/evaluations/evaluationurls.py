from collections.abc import Iterable
from mycrawling.parse.urlcontentsparse import ParseUrls
from .base import ScoreEvaluations
from mycrawling.scorings.urls import ScoringUrls
from mycrawling.logs.debug_log import debug_logger


class EvaluateUrls(ParseUrls, ScoreEvaluations):
    ''' urlスコアに基づいて評価。 '''

    def evaluate_hostname(self, current_url, urls):
        ''' 
        urlのhostnameとcurrent_urlのhostnameを比較。
        対象urlのhostnameとcurrent_hostnameが一致か又は対象urlが相対urlパスだった場合、同じサイト内urlとしてTrueを返す。 
        
        '''

        result = False
        if current_url == urls:
            #current_url とurlsが完全一致ならば直ちにTrueを返す。
            result = True
            return result        
        hostname_dict = self.hostname_parse(*(current_url, urls))
        current_hostname = hostname_dict.pop(current_url)
        urls_hostname = hostname_dict.pop(urls)
        debug_logger.debug(f'current_hostname: {current_hostname} | urls_hostname: {urls_hostname}')
        result_urls_hostname = urls_hostname is None

        urls_hostname_is_current_hostname = urls_hostname == current_hostname

        #urlsにhostnameが無い又はcurrent_hostnameと一致した場合、同サイト内と見做す。
        result = result_urls_hostname or urls_hostname_is_current_hostname
        
        return result
    
    def evaluate_score(self, scorer_type=None, score=None, *args, **kwargs):

        #urlsのhostnameとcurrent_urlのhostnameの一致評価。Noneの場合hostnameを評価対象に含まない。
        name_is_current_name = kwargs.pop('name_is_current_name', None)

        if isinstance(score, Iterable):
            statistics = kwargs.pop('statistics', 'rate')
            statistics_value = ScoringUrls.urls_statistics(score, statistics=statistics)
            score = statistics_value

        result = super().evaluate_score(scorer_type, score, *args, **kwargs)
        urls_result = result and (name_is_current_name is True or name_is_current_name is None)
        
        debug_logger.debug(f'name_is_current_name: {name_is_current_name}')
        return urls_result

