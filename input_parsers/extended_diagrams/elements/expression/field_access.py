from . import Expression, This
from .method_invocation import Width


class FieldAccess(Expression):
    tag_name: str = "expression_field_access"
    field_name: str
    target: Expression

    def __init__(self, field_name: str = None, target: Expression = None):
        super().__init__()
        if target is None:
            target = This()
        self.field_name = field_name
        self.target = target

    def width(self):
        return Width(self)

    def value(self):
        return self

    def get_attributes(self):
        attributes = super().get_attributes()
        if self.field_name is not None:
            attributes["field_name"] = self.field_name

    def children_to_xml(self, element):
        element.append(self.target.to_xml())
