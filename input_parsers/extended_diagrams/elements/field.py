from lxml import etree
from .expression import Expression
from input_parsers.extended_diagrams.protocol.element.exception import InconsistentData
from typing import List, Dict

from rfc2xml.elements import Element


class Field(Element):
    tag_name: str = "field"
    name: str = None
    abbrv: str = None
    width: int = None
    expressions: List['Expression'] = []
    type: str = None
    value: int = None
    array: bool = None

    def __init__(self, name: str = None, abbrv: str = None, width: int = None, expressions: List['Expression'] = None,
                 type: str = None, value: int = None, array: bool = None):
        super().__init__()
        if expressions is None:
            expressions = []
        self.name = name
        self.abbrv = abbrv
        self.width = width
        self.type = type
        self.value = value
        self.array = array
        self.expressions = expressions

    def get_attributes(self):
        attributes = {}
        if self.name is not None:
            attributes["name"] = self.name
        if self.abbrv is not None:
            attributes["abbrv"] = self.abbrv
        if self.width == -1:
            attributes["width"] = "variable"
        elif self.width is not None:
            attributes["width"] = str(self.width)
        if self.type is not None:
            attributes["type"] = str(self.type)
        if self.value is not None:
            attributes["value"] = str(self.value)
        if self.array is not None:
            attributes["array"] = str(self.array)
        return attributes

    def to_xml(self):
        element = etree.Element(str(self.tag_name), self.get_attributes())
        for expression in self.expressions:
            element.append(expression.to_xml())
        return element

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
        return self

    def set_name(self, name: str):
        self.name = name.strip()
        return self

    def set_abbrv(self, abbrv: str):
        self.abbrv = abbrv
        return self

    def set_width(self, width: int):
        self.width = width
        return self

    def add_expression(self, expression: 'Expression'):
        self.expressions.append(expression)
        return self
