from pathlib import Path
from urllib.parse import urlparse


def join_current_dir(path, relative=False):
    
    current_path = Path.cwd()
    if relative is True:
        current_path = Path(current_path.name)
    path = Path(path)
    return current_path.joinpath(path)


def join_path(*args):
    ''' パスを連結していく。 '''
    first = True
    path = ''
    for arg in args:

        if first is True:
            path = Path(arg)
            first = False
            continue
        path_obj = Path(arg)
        path = path.joinpath(path_obj)
    
    return path
    

def match_urls(url1, url2):
    '''
    2つのurlが一致するか評価する。 
    末尾に於ける/の有無は、ルートurlにかんしては有無に関わらず同一と見做し、それ以外は別のurlとして判定する。
    '''
    result = False

    if url1 == url2:
        result = True
        return result
    
    parsed_url1 = urlparse(url1)
    parsed_url2 = urlparse(url2)
    root_url1 = parsed_url1.scheme + '://'+ parsed_url1.hostname
    root_url2 = parsed_url2.scheme + '://' + parsed_url2.hostname
    if root_url1 == root_url2:
        if (parsed_url1.path == parsed_url2.path) or (parsed_url1.path in {'', '/'} and parsed_url2.path in {'', '/'}):
            result = True
        else:
            result = False
        if result and parsed_url1.query == parsed_url2.query:
            pass
        else:
            result = False
            
        if result and parsed_url1.netloc == parsed_url2.netloc and parsed_url1.port == parsed_url2.port:
            pass
        else:
            result = False
    else:
        result = False
    return result        


