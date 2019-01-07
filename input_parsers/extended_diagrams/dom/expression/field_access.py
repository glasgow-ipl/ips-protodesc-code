from . import Expression, This
from .method_invocation import Width


class FieldAccess(Expression):
    field_name: str
    target: Expression

    def __init__(self, field_name: str=None, target: Expression=None):
        if target is None:
            target = This()
        self.field_name = field_name
        self.target = target

    def to_dict(self):
        return {
            "expression": "FieldAccess",
            "target": self.target.to_dict(),
            "field_name": self.field_name
        }

    def get_field_names(self):
        return [self.field_name]

    def width(self):
        return Width(self)

    def value(self):
        return self