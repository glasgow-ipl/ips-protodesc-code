from ..expression import Expression
from . import Element
from .exception import InconsistentData
from typing import List, Dict


class Field(Element):
    name: str = None
    abbrv: str = None
    width: int = None
    expressions: List['Expression'] = []
    type: str = None
    value: int = None
    array: bool = None

    def __init__(self, name: str = None, abbrv: str = None, width: int = None, expressions: List['Expression'] = [],
                 type: str = None, value: int = None, array: bool = None):
        self.name = name
        self.abbrv = abbrv
        self.width = width
        self.expressions = expressions
        self.type = type
        self.value = value
        self.array = array

    def to_dict(self):
        return {
            **super(Field, self).to_dict(),
            "attributes": {
                "name": self.name,
                "abbrv": self.abbrv,
                "width": self.width,
                "expr": Expression.list_to_dict(self.expressions),
                "type": self.type,
                "value": self.value,
                "array": self.array,
            }
        }

    @staticmethod
    def merge_field_values(value1, value2, prefer_left: bool = False):

        if prefer_left:
            if value1 is not None:
                return value1
            else:
                return value2

        if value1 is None:
            return value2
        elif value2 is None:
            return value1
        elif value1 == value2:
            return value1
        else:
            raise InconsistentData(
                str(value1) + " and " + str(value2) + " given",
                value1=value1,
                value2=value2
            )

    def merge_field(self, field: 'Field', name: str, prefer_field: bool = False):
        try:
            setattr(self, name, self.merge_field_values(getattr(field, name), getattr(self, name), prefer_field))
        except InconsistentData as error:
            raise error.update(attribute=name)

    def merge(self, field: 'Field'):
        try:
            self.merge_field(field, 'name')
            self.merge_field(field, 'abbrv')
            self.merge_field(field, 'width')
            self.merge_field(field, 'expressions', True)
            self.merge_field(field, 'type')
            self.merge_field(field, 'value')
            self.merge_field(field, 'array')
        except InconsistentData as error:
            raise error.update(field=field.name)

    def __repr__(self):
        return str(self.to_dict())

    def get_definitions_dict(self) -> List[Dict]:
        definitions = []
        for expression in self.expressions:
            for definition in expression.get_definitions():
                definition_dict = definition.to_dict()
                if definition_dict not in definitions:
                    definitions.append(definition_dict)
        return definitions
