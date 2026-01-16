import dataclasses
from mycrawling.datas.base import BaseDataClass


@dataclasses.dataclass()
class RobotsParseDataList(BaseDataClass):
    prohibition_url_list : list = dataclasses.field(default_factory=list)

