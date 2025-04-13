import dataclasses

from mycrawling.datas.base import BaseDataClass

#Var37.06.14.15a(24/07/25/時点のバージョン)

@dataclasses.dataclass()
class FilterDataList(BaseDataClass):
    filtering_item: dict

