from inspect import Signature, signature
from inspect import Parameter, _empty, BoundArguments
from collections.abc import Iterable
from collections import deque
from typing import Union, List, Dict
from types import MappingProxyType
from mycrawling.logs.debug_log import debug_logger

def run_method(arguments, method, **kwargs):
    ''' メソッドにパラメータを渡して実行する。argumentsに何も渡さない場合は、空のコレクション型を渡す。'''

    debug_logger.debug(f'arguments:{arguments} | method: {method} | kwargs:{kwargs}')
    importance_keys = kwargs.pop('importance_keys', list())
    args, kwargs = prepare_arguments(arguments, method, importance_keys=importance_keys)
    debug_logger.debug(f'result prepare_arguments. args: {args} | kwargs: {kwargs}')

    return method(*args, **kwargs)


''' argumentsの検証と整形。 '''
def edit_keyword_argument(arguments:List, keywords):
    ''' argumentsにキーワード引数を追加又は編集する。 '''
    if not isinstance(keywords, dict):
        raise TypeError('keyowrdsは辞書型のみを受けとります。')
    
    if isinstance(arguments, tuple):
        #タプルの場合、値の追加が出来ない為ここで型変換する。
        arguments = list(arguments)
    elif isinstance(arguments, dict):
        arguments = [arguments]

    if isinstance(arguments, (str, bytes)) or not isinstance(arguments, Iterable):
        arguments = [arguments]
        arguments.append(keywords)
    elif isinstance(arguments, list) and not any(isinstance(arg, dict) for arg in arguments):
        #argumentsがイテラブルオブジェクト且つ内部に辞書型アイテムを保持していない場合、新規辞書としてkeywordsを追加する。
        arguments.append(keywords)

    elif isinstance(arguments, Iterable):
        #イテラブルオブジェクトに辞書型アイテムが存在した場合、最初に出現した辞書型アイテムをアップデートをする。
        for arg in arguments[:]:
            if isinstance(arg, dict):
                arg.update(keywords)
                break

    debug_logger.debug(f'arguments: {arguments}')
    return arguments


def edit_word_argument(arguments:List, value, **kwargs):
    ''' 任意の位置に位置引数値を挿入する。デフォルトでは、最後尾、キーワード引数アイテムの直前'''
    index = kwargs.pop('index', None)

    if isinstance(arguments, tuple):
        arguments = list(arguments)
    elif isinstance(arguments, (str, bytes, dict)) or not isinstance(arguments, Iterable):
        arguments = [arguments]
    
    if index:
        arguments.insert(index, value)
    elif any(isinstance(arg, dict) for arg in arguments):
        for index, argument in enumerate(arguments[:]):
            if isinstance(argument, dict):
                arguments.insert(index, value)
                break
    else:
        arguments.append(value)
    return arguments


def isiterable(item):
    ''' アイテムが str, bytesを除いたイテラブルオブジェクトかどうか判定する。'''
    result = False
    if not isinstance(item, (str, bytes)) and isinstance(item, Iterable):
        result = True
    return result


''' methodのシグネチャを解析する '''
def method_signature(method, attrs=None):
    '''methodのシグネチャを解析する。デフォルトではSignatureオブジェクトを返す。特定の属性を返す場合はattrsに指定。'''

    sig = None
    if not callable(method):
        raise TypeError('引数"method"は、呼び出し可能オブジェクトのみを受け取ります。')
    if isinstance(method, Signature):
        sig = method
    elif callable(method):
        sig = signature(method)

    if attrs and hasattr(sig, attrs):
        sig_attr = getattr(sig, attrs)
        return sig_attr
    elif attrs and not hasattr(sig, attrs):
        raise AttributeError(f'シグネチャに存在しない属性です。| {attrs}')
    
    return sig


def method_parameter_parse(method):
    ''' 関数のシグネチャからパラメータ情報を取得。 '''

    if not callable(method):
        raise TypeError('methodが受け取るのは関数です。')
    
    if not isinstance(method, Signature):
        method_sig = signature(method)
        return method_sig.parameters
    
    else:
        return method.parameters


def get_sig_parameters_kinds(signature_parameters:Union[MappingProxyType, Signature]):
    ''' メソッドのシグネチャから取得した各パラメータ(inspect.Parameterオブジェクト)のkind属性を返す。 '''
    parameter_kinds = dict()
    parameters = None

    if isinstance(signature_parameters, Signature):
        #Signatureオブジェクトの場合はparameter属性を取得
        parameters = signature_parameters.parameters

    elif isinstance(signature_parameters, (MappingProxyType, dict)) and all(isinstance(p, Parameter) for p in signature_parameters.values()):
        #辞書又はmappingproxyの場合は、中身が全てParameterオブジェクトである事を確認。
        parameters = signature_parameters

    elif isinstance(signature_parameters, Iterable) and all(isinstance(p, Parameter) for p in signature_parameters):
        
        parameter_kinds = {p.name: p.kind for p in signature_parameters}
        return parameter_kinds
    
    if not parameters:
        return parameter_kinds
    
    parameter_kinds = {name: param.kind for name, param in parameters.items()}
    
    return parameter_kinds


def get_parameters_names(obj):
    ''' オブジェクトからパラメータ名を取得する。 戻り値はリスト型
    '''
    parameter_names = []
    
    if not isinstance(obj, Signature) and callable(obj):
        obj = signature(obj)
        
    if isinstance(obj, (MappingProxyType, dict)):
        parameter_names = list(obj.keys())
    
    elif isinstance(obj, Signature):
        parameter_names = list(obj.parameters.keys())
    
    elif isinstance(obj, BoundArguments):
        parameter_names = list(obj.arguments.keys())

    elif isinstance(obj, Parameter):
        parameter_names = [obj.name]

    elif isinstance(obj, Iterable) and all(isinstance(o, Parameter) for o in obj):
        parameter_names = [o.name for o in obj]
    else:
        raise TypeError('値を取得できません。Signature, BoundArguments, Parameterのいずれかを渡してください。')
    
    return parameter_names


def has_param_type(parameter_obj, type_name):
    ''' 指定したパラメータタイプがシグネチャから取得したパラメータタイプ情報の中に存在するか評価する。 '''
    parameter_kinds = get_sig_parameters_kinds(parameter_obj)

    return type_name in parameter_kinds.values()

    
def has_param_names(parameter_obj, name):
    ''' 引数名がmethodのシグネチャに含まれているか評価する。 '''
    if isinstance(parameter_obj, (list, tuple, set)):
        return name in parameter_obj
    parameter_names = get_parameters_names(parameter_obj)

    return name in parameter_names
            

def param_type_count(*type_name, parameter_obj):
    ''' 指定したパラメータタイプがシグネチャから取得したパラメータタイプ情報の中に何個存在するか評価する。'''
    length_param_types = {}#其々のパラメータタイプの型数を辞書で返す。
    parameter_kinds = get_sig_parameters_kinds(parameter_obj)

    kinds_list = list(p.name for p in parameter_kinds.values())
    length_param_types = {name: kinds_list.count(name) for name in type_name}

    return length_param_types


''' methodに実引数を割り当てる処理。 '''
def split_arg_kwags(arguments):
    '''
        実引数を位置引数とキーワード引数に分割しリストと辞書型のタプルで返す。但し、辞書型が複数含まれていた場合は、
        最後の辞書型をキーワード引数とし、他は位置引数に吸収される。 
        引数構成によっては位置引数のみ、キーワード引数のみにまとめられる。
    '''

    positionals, kwargs = list(), dict()

    if isinstance(arguments, dict):
        kwargs = arguments
        return positionals, kwargs
    
    elif not isinstance(arguments, (str, bytes)) and isinstance(arguments, Iterable):

        last_kwgs_index = None
        kwargs_index = [index for index, args in enumerate(arguments) if isinstance(args, dict)]#キーワード(辞書型アイテム)のインデックスを保持。
        if kwargs_index:
            kwargs_index.sort()
            last_kwgs_index = kwargs_index[-1]
        
        for index, args in enumerate(arguments):
            if isinstance(args, dict) and index == last_kwgs_index:
                kwargs = args

            else:
                positionals.append(args)

    elif isinstance(arguments, (str, bytes)) or not isinstance(arguments, Iterable):
        positionals.append(arguments)
    
    return positionals, kwargs


def positional_arg_handling(parameter_obj, arg=None, keyword_param=None):
    ''' 位置引数とmethodのパラメータ値を検証し、該当する値を評価する。'''
    '''
    位置引数の有無を確認し、Noneの場合は実引数の内キーワード引数に該当値が無いか検証する。また位置引数値とキーワード引数が
    重複しない様にもする。
    '''
    if not isinstance(parameter_obj, Parameter):
        raise TypeError('parameter_objはParameterオブジェクトを受け取ります。')
    if keyword_param is None:
        keyword_param = dict()
    parameter_name = parameter_obj.name
    parameter_default = parameter_obj.default

    if arg is None and parameter_name in keyword_param:
        arg = keyword_param.pop(parameter_name)
        return arg
    elif arg and parameter_name in keyword_param:

        del keyword_param[parameter_name]

    elif arg is None and parameter_default is not _empty:

        return parameter_default

    return arg


def prepare_arguments(arguments, method:Union[List, Dict], importance_keys=set()):

    importance_keys = importance_keys if isinstance(importance_keys, (set, list)) else set()

    arranged_args = list()#位置引数を並べて保持する。
    arranged_kwargs = dict()#キーワード引数を保持する。
    if isinstance(method, Signature) or callable(method):
        method_parameters = method_parameter_parse(method)
    elif isinstance(method, (dict, MappingProxyType)) and all(isinstance(p, Parameter) for p in method):
        method_parameters = method
    else:
        raise TypeError('methodはSignature, 関数, 辞書, MappingProxyTypeを受け取ります。')
    has_ver_positional = has_param_type(method_parameters, Parameter.VAR_POSITIONAL)#可変長位置引数の存在を判定。

    method_parameter_objects = method_parameters.values()#ParametersからParameterオブジェクトリストを取得
    len_positional_params = sum(param_type_count('POSITIONAL_ONLY', 'POSITIONAL_OR_KEYWORD', parameter_obj=method_parameter_objects).values())

    args, kwgs = split_arg_kwags(arguments)#実引数を位置引数,キーワード引数に分割する。
    args_deq = deque(args)
    kwgs_argument = kwgs.copy()

    for param_obj in method_parameter_objects:
        param_name = param_obj.name
        param_kind = param_obj.kind

        if param_kind == Parameter.VAR_POSITIONAL:
            arranged_args += args_deq
            args_deq.clear()
            if param_name in kwgs_argument.keys():
                #可変長位置引数名がキーワード引数にもある場合は追加する。
                var_positional_values = positional_arg_handling(param_obj, keyword_param=kwgs_argument)            
                if isiterable(var_positional_values):
                    for value in var_positional_values:
                        arranged_args.append(value)
                else:
                    arranged_args.append(var_positional_values)
            continue

        elif param_kind == Parameter.VAR_KEYWORD:
            arranged_kwargs.update(kwgs_argument)
            continue


        if not args_deq and param_obj.default == _empty and param_name not in kwgs_argument:
            raise TypeError(f'引数の数が足りません。| parameter name: {param_name}')
        match param_name in importance_keys:
            #キーワード引数優先の場合はkwgsから該当する値を取得。
            #位置引数をそのまま用いる場合はargs_deqから取得。
            case True if param_name in kwgs_argument:
                args_item = kwgs_argument.pop(param_name)
            case False:
                args_item = args_deq.popleft() if args_deq else None

        if param_kind in {Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD}:
            
            positional_arg_value = positional_arg_handling(param_obj, args_item, kwgs_argument) 
            arranged_args.append(positional_arg_value)

        elif param_kind == Parameter.KEYWORD_ONLY:
            match param_name in kwgs_argument:
                case True:
                    arranged_kwargs[param_name] = kwgs_argument.pop(param_name)
                case False if args_item:
                    arranged_kwargs[param_name] = args_item

    if not has_ver_positional and len(arranged_args) > len_positional_params:
        raise TypeError('位置引数の数が多すぎます。')
    
    return arranged_args, arranged_kwargs


