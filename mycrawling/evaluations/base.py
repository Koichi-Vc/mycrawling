from mycrawling.logs.debug_log import debug_logger
''' スコア値をscorerアルゴリズム、符号に合わせてラップする。 '''

#Var37.06.14.15a(24/07/25/時点のバージョン)

class ScoreEvaluations:
    ''' スコアを評価 '''
    
    def __num_symbol_decorator(func):
        """ 数値符号をアルゴリズムに合わせて操作する"""

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

            debug_logger.debug(f'after-- scorer: {scorer} score: {score} | scorer_type: {scorer_type}')
            result = func(self, scorer_type, score, add_subst=add_subst, comp_num=comp_num, *args, **kwargs)
            debug_logger.debug(f'result: {result}')
            return result

        return wrapper


    @__num_symbol_decorator
    def score_cutoff_init_(self, scorer_type=None, score=None, *args, **kwargs):
        """ socreの初期値をアルゴリズムに合わせて定義する"""

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
    def scorering_complement_value(self,
                                   scorer_type=None,
                                   score=None,
                                   add_subst='add',
                                   comp_num=0, *args, **kwargs):
        ''' スコアに追加で値を上乗せをする。 '''
        '''
        <comp_num> 
        distance:加算ならばscore - comp_num,減算ならscore + comp_num
        similarlity: 加算ならばscore + comp_num, 減算ならscore - comp_num
        ratio:
            int型の場合: 加算ならばscore + comp_num, 減算ならscore - comp_num
            
            float型の場合: 100をmaxとした場合の割合と解釈し、加算減算評価する。
        '''
        if not score:
            #scoreがNoneだった場合、初期値をセットする。
            score = self.score_cutoff_init_(scorer_type=scorer_type)

        if 'distance' == scorer_type:
            comp_num = comp_num * -1
        elif 'similarlity' == scorer_type:
            comp_num = abs(comp_num)

        elif 'ratio' == scorer_type and isinstance(comp_num, float):
            ''' ratio系且つcomp_numがfloat型の場合、ratio系最高スコア100に対する割合と解釈 '''
            comp_num = 100*comp_num
        
        if add_subst == 'add':
            score += comp_num
        elif add_subst == 'subt' or add_subst == 'subtraction':
            score -= comp_num

        return score


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

