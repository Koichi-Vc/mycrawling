import dataclasses
from mycrawling.datas.base import BaseDataClass



@dataclasses.dataclass()
class FilterDataList(BaseDataClass):
    filtering_item: dict

