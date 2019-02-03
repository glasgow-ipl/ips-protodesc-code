from typing import List


class Dictionarable:

    def to_dict(self):
        return {}

    @staticmethod
    def list_to_dict(elements: List['Dictionarable']):
        out = []
        if elements is None:
            return out
        for element in elements:
            out.append(element.to_dict())
        return out
