from typing import List
from ..construct import Construct
from ..dictionarable import Dictionarable


class Expression(Dictionarable):

    @staticmethod
    def get_field_names():
        return []

    def get_definitions(self) -> List[Construct]:
        return []

    @staticmethod
    def list_to_dict(elements: List['Expression']):
        out = []
        for element in elements:
            out.append(element.to_dict())
        return out
