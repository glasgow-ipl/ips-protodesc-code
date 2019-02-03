from typing import List
from input_parsers.extended_diagrams.dictionarable import Dictionarable


class Element(Dictionarable):

    def get_name(self):
        return self.__class__.__name__

    def to_dict(self):
        return {
            "type": self.get_name()
        }

    @staticmethod
    def list_to_dict(elements: List['Element']):
        out = []
        for element in elements:
            out.append(element.to_dict())
        return out
