from ..dictionarable import Dictionarable
from typing import Dict


class Other(Dictionarable):
    value: Dict = None

    def __init__(self, value: Dict = None):
        self.value = value

    def to_dict(self):
        return {
            "name": "other",
            "value": self.value
        }
