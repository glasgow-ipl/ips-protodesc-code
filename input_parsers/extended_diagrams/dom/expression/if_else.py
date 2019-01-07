from . import Expression, Empty
from typing import List
from ..construct import Construct


class IfElse(Expression):
    condition: 'Expression'
    if_true: 'Expression'
    if_false: 'Expression'

    def __init__(self, condition: 'Expression'=None, if_true: 'Expression'=None, if_false: 'Expression'=None):
        if condition is None:
            condition = Empty()
        if if_true is None:
            if_true = Empty()
        if if_false is None:
            if_false = Empty()

        self.condition = condition
        self.if_true = if_true
        self.if_false = if_false

    def to_dict(self):
        return {
            "expression": "IfElse",
            "condition": self.condition.to_dict(),
            "if_true": self.if_true.to_dict(),
            "if_false": self.if_false.to_dict()
        }

    def get_definitions(self) -> List[Construct]:
        return self.condition.get_definitions() + self.if_true.get_definitions() + self.if_false.get_definitions()
