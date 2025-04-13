import dataclasses

#Var37.06.14.15a(24/07/25/時点のバージョン)

@dataclasses.dataclass()
class PageScoreStatisticsSet():
    ''' スコアから算出した統計情報を保持しておく為のクラス。 '''
    instance_reqd_fields = ['reqd_detection_primary_texts',
                            'reqd_detection_highscore_texts',
                            'reqd_primary_texts_count',
                            'reqd_highscore_texts_count',
                            'reqd_all_high_score_rate']
    
    evaluated_text_score_statistics_attrs_name = [
        'eval_primary_text_types',
        'eval_highscore_text_types',
        'eval_primary_text_count',
        'eval_highscore_text_count',
        'eval_primary_or_highscore_text_count',
        'eval_all_high_score_rate'
    ]
    
    child_length: int = dataclasses.field(default=0)#その要素が保持する直接の子要素の総数
    child_count: int = dataclasses.field(default=0)#その要素が保持する直接の子要素の内テキストを検出した子要素の数
    detection_highscore_count: int = dataclasses.field(default=0)
    detection_highscore_text: set = dataclasses.field(default_factory=set)
    detection_primary_count: int = dataclasses.field(default=0)
    detection_primary_text: set = dataclasses.field(default_factory=set)

    __evaluated_statistics_socre: dict = dataclasses.field(default_factory=dict)
    
    @property
    def evaluated_statistics_socre(self):
        
        return self.__evaluated_statistics_socre

    def add_evalated_text_score_statistics(self, *evaluated_values):
        for attrs_name, value in zip(*[self.evaluated_text_score_statistics_attrs_name, evaluated_values]):
            self.__evaluated_statistics_socre.setdefault(attrs_name, value)
    

    def text_score_statistics_eval(self, instance):
        ''' 要素内の子要素に含有していた全ての高類似度テキスト '''
        ''' 検出したスコア・統計情報を元に閾値条件の評価をする。 '''
        #all_target_score = detection_highscore_count+detection_primary_count
        #detection_texts_types_countの修正
        #検出された重要語彙の種類数を評価

        is_attrs = all(hasattr(instance, reqd) for reqd in self.instance_reqd_fields)

        if not is_attrs:
            raise AttributeError('要素評価に必要な閾値を参照できませんでした。')
        
        eval_primary_text_types = len(self.detection_primary_text) >= instance.reqd_detection_primary_texts
        #検出された高類似度語彙の種類数を評価
        eval_highscore_text_types = len(self.detection_highscore_text) >= instance.reqd_detection_highscore_texts
        
        #primary_count, highscore_countの修正
        #検出された重要語彙自体の数を評価
        eval_primary_text_count = self.detection_primary_count >= instance.reqd_primary_texts_count
        #検出された高類似度語彙自体の数を評価
        eval_highscore_text_count = self.detection_highscore_count >= instance.reqd_highscore_texts_count

        #検出された重要語彙か又は高類似度語彙の数を評価
        eval_primary_or_highscore_text_count = eval_primary_text_count or eval_highscore_text_count

        eval_all_high_score_rate = False
        if self.child_count >= 1:
            all_high_score_rate = (self.child_count / self.child_length)*100
            eval_all_high_score_rate = all_high_score_rate >= instance.reqd_all_high_score_rate
        self.add_evalated_text_score_statistics(eval_primary_text_types,
                                                eval_highscore_text_types,
                                                eval_primary_text_count,
                                                eval_highscore_text_count,
                                                eval_primary_or_highscore_text_count,
                                                eval_all_high_score_rate)
        return self.evaluated_statistics_socre


    @classmethod
    def create_dataclass(cls, *args, **kwargs):
        #クラスインスタンスを生成
        return cls(*args, **kwargs)

