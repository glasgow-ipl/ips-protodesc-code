from . import Expression
from ..construct import Construct
from typing import Dict, List


class Other(Expression):
    value: Expression = None

    def __init__(self, value: Expression = None):
        self.value = value

    def get_definitions(self) -> List[Construct]:
        return self.value.get_definitions()

    def to_dict(self):
        value = None
        if self.value is not None:
            value = self.value.to_dict()

        return {
            "name": "other",
            "value": value
        }