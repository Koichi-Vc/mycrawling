import dataclasses
from mycrawling.datas.base import BaseDataClass

#Var37.06.14.15a(24/07/25/時点のバージョン)

@dataclasses.dataclass()
class RobotsParseDataList(BaseDataClass):
    prohibition_url_list : list = dataclasses.field(default_factory=list)

