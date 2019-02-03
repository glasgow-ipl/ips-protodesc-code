from typing import List
from input_parsers.extended_diagrams.ir.construct import Construct
from input_parsers.extended_diagrams.dictionarable import Dictionarable


class Expression(Dictionarable):

    @staticmethod
    def get_field_names():
        return []

    def get_definitions(self) -> List[Construct]:
        return []

    @staticmethod
    def list_to_dict(elements: List['Expression']):
        out = []
        if elements is None:
            return out
        for element in elements:
            out.append(element.to_dict())
        return out
