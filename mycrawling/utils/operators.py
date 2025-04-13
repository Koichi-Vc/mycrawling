
#Var37.06.14.15a(24/07/25/時点のバージョン)

class SelectListOperator:
    ''' リスト全体の論理演算メソッドを指定 '''
    operator_and = {'and', 'AND'}
    operator_or = {'or' , 'OR'}
    operator_nand = {'not and','nand','NAND'}
    operator_nor = {'not or', 'NOR', 'nor'}
    
    @classmethod
    def select_operator(cls, list_operator_type=any):

        if callable(list_operator_type):
            list_operator = list_operator_type
        elif hasattr(cls, list_operator_type):
            list_operator = getattr(cls, list_operator_type)
        
        elif list_operator_type in cls.operator_and:
            list_operator = all
        elif list_operator_type in cls.operator_or:
            list_operator = any
        elif list_operator_type in cls.operator_nand:
            list_operator = cls.not_and
        elif list_operator_type in cls.operator_nor:
            list_operator = cls.not_or
        
        return list_operator


    def not_and(self, *result_list):
        ''' 配列に対してNAND評価 '''
        return not all(result_list)
      
    def not_or(self, *result_list):
        '''配列に対してNOR評価 '''
        return not any(result_list)

