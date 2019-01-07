from . import Expression
from ..construct import Int, Construct
from typing import List


class Constant(Expression):
    value: int = None
    size: int = 32

    def __init__(self, value=None):
        self.value = value

    def get_type(self):
        return "Int$" + str(self.size)

    def to_dict(self):
        return {
            "expression": "Constant",
            "type": self.get_type(),
            "value": self.value
        }

    def get_definitions(self) -> List[Construct]:
        return [
            Int(self.size)
        ]
