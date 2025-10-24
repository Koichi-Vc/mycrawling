import dataclasses
from re import search
from .base import BaseDataClass
from mycrawling.logs.debug_log import debug_logger


@dataclasses.dataclass()
class Reference_Title_A_Url_Texts(BaseDataClass):
    
    reference_texts: set = dataclasses.field(default_factory=set)
    reference_urls: set = dataclasses.field(default_factory=set)
    
    #データクラスで保持したテキストが含まれているかを調べるメソッド
    def texts_is_contain(self, texts):
        ''' textsにreference_textsのテキストが含まれるか評価する。 '''
        result = False
        debug_logger.debug(f'text: {texts} | reference_texts: {self.reference_texts}')
        for refer_txt in self.reference_texts:
            if refer_txt in texts:
                result = True
                break
        return result

    def urls_is_contain(self, urls):
        ''' urlsにreference_urlsのテキストが含まれるか評価する。 '''
        result = False
        for refer_url in self.reference_urls:
            if refer_url in urls:
                result = True
                break
        return result


@dataclasses.dataclass()
class Reference_TextCollection(BaseDataClass):
    
    jp_standard_texts: list = dataclasses.field(default_factory=list)
    jp_primary_texts: set = dataclasses.field(default_factory=list)
    en_standard_texts: list = dataclasses.field(default_factory=list)
    en_primary_texts: set = dataclasses.field(default_factory=list)
    
    jp_all_texts: list = dataclasses.field(init=False)
    en_all_texts: list = dataclasses.field(init=False)
    all_standard_texts: list = dataclasses.field(init=False)

    all_primary_texts: list = dataclasses.field(init=False)
    all_reference_text_list: list = dataclasses.field(init=False)

    def __post_init__(self):
        self.jp_all_texts = self.jp_standard_texts + list(self.jp_primary_texts)
        self.en_all_texts = self.en_standard_texts + list(self.en_primary_texts)
        self.all_standard_texts = list(self.jp_standard_texts) + list(self.en_standard_texts)
        self.all_primary_texts = list(self.jp_primary_texts)+list(self.en_primary_texts)
        self.all_reference_text_list = self.jp_all_texts+self.en_all_texts

    def get_all_fields(self):
        field_dict = { field:value for field, value in vars(self).items() if bool(search(r'text', field))}
        return field_dict

