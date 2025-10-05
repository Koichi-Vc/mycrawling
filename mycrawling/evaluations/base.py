from mycrawling.logs.debug_log import debug_logger

''' スコア値をscorerアルゴリズム、符号に合わせてラップする。 '''


class ScoreEvaluations:
    ''' スコアを評価 '''
    
    def __num_symbol_decorator(func):
        ''' 数値符号をアルゴリズムに合わせて操作する'''

        def wrapper(self, scorer=None, score=None, *args, **kwargs):
            """ 
            <パラメータ>
            add_subst: 加算か減算を指定する。addなら加算,subst or substractionなら減算
            comp_num: 加点,減点する値を指定。
            """
            debug_logger.debug(f'before-- func: {func} | args: {args}| kwargs:{kwargs} | before; scorer: {scorer}| score: {score} ')
            
            add_subst = kwargs.pop('add_subst', 'add')
            comp_num = kwargs.pop('comp_num', 0)
            scorer_type = None

            if scorer:
                if not isinstance(scorer, str):
                    scorer_name = getattr(scorer,'__name__',None)
                else:
                    scorer_name = scorer
                if not scorer_name:
                    scorer_name = str(scorer)
                scorer_name = scorer_name.casefold()
                
                if 'distance' in scorer_name:
                    scorer_type = 'distance'
                elif 'similarlity' in scorer_name:
                    scorer_type = 'similarlity'
                elif 'ratio' in scorer_name:
                    scorer_type = 'ratio'

            result = func(self, scorer_type, score, add_subst=add_subst, comp_num=comp_num, *args, **kwargs)
            
            debug_logger.debug(f'after-- scorer: {scorer} score: {score} | scorer_type: {scorer_type}')
            debug_logger.debug(f'result: {result}')
            return result

        return wrapper

    
    @__num_symbol_decorator
    def score_cutoff_init_(self, scorer_type=None, score=None, *args, **kwargs):
        ''' socreの初期値をアルゴリズムに合わせて定義する'''

        custom_initvalue = kwargs.pop('custom_initvalue', '')

        if custom_initvalue != '':
            #初期値を明示的に指定する
            result = custom_initvalue
            return result
        
        if 'distance' == scorer_type:
            result = 1
        else:
            result = 0
        return result


    @__num_symbol_decorator
    def evaluate_score(self, scorer_type=None, score=None, *args, **kwargs):
        ''' scorer_typeに基づく境界値に対するスコアの真偽を評価 '''        
        result = False
        boundary = kwargs.pop('boundary', self.score_cutoff_init_(scorer_type))
        debug_logger.debug(f'score: {score} | scorer_type: {scorer_type} | boundary: {boundary}')
        if scorer_type == 'distance':
            result = score <= boundary
        else:
            result = score >= boundary

        return result

