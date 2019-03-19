from lxml import etree
from .expression import Expression
from ..exception import InconsistentDataException
from typing import List
from rfc2xml.elements import Element
from protocol import Expression as ProtocolExpression, MethodInvocationExpression, FieldAccessExpression,\
    ArgumentExpression, ThisExpression, ConstantExpression, Protocol


class Field(Element):
    tag_name: str = "field"
    name: str = None                        # The name of the field
    abbrv: str = None                       # An abbreviated name for this field
    width: int = None                       # The size of this field
    expressions: List['Expression'] = []    # The expressions attached to this field
    type: str = None                        # The type of this field
    value: int = None                       # The value of this field
    optional: bool = False                  # Whether this field is optional

    def __init__(self, name: str = None, abbrv: str = None, width: int = None, expressions: List['Expression'] = None,
                 type: str = None, optional: bool = False, value: int = None):
        super().__init__()
        if expressions is None:
            expressions = []
        self.name = name
        self.abbrv = abbrv
        self.width = width
        self.type = type
        self.optional = optional
        self.value = value
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
        if self.optional:
            attributes["optional"] = str(self.optional)
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
            raise InconsistentDataException(
                str(value1) + " and " + str(value2) + " given",
                value1=value1,
                value2=value2
            )

    def merge_field(self, field: 'Field', name: str, prefer_field: bool = False):
        try:
            setattr(self, name, self.merge_field_values(getattr(field, name), getattr(self, name), prefer_field))
        except InconsistentDataException as error:
            raise error.update(attribute=name)

    def merge(self, field: 'Field', ignore_value: bool = False) -> 'Field':
        try:
            self.merge_field(field, 'name')
            self.merge_field(field, 'abbrv')
            self.merge_field(field, 'width')
            self.merge_field(field, 'expressions', True)
            self.merge_field(field, 'type')
            self.merge_field(field, 'optional', True)
            if not ignore_value:
                self.merge_field(field, 'value')
        except InconsistentDataException as error:
            raise error.update(field=field.name)
        return self

    def set_value(self, value: int):
        self.value = value
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

    def set_type(self, type: str):
        self.type = type
        return self

    def set_optional(self, optional: bool):
        self.optional = optional
        return self

    def add_expression(self, expression: 'ProtocolExpression'):
        self.expressions.append(Expression(expression))
        return self

    def to_protocol_expressions(self, protocol: 'Protocol'):
        output = []
        for expression in self.expressions:
            output.append(expression.expression)
        if self.value is not None:
            output.append(
                MethodInvocationExpression(
                    MethodInvocationExpression(
                        FieldAccessExpression(
                            ThisExpression(),
                            self.name
                        ),
                        "to_integer",
                        []
                    ),
                    "eq",
                    [
                        ArgumentExpression(
                            "other",
                            ConstantExpression(
                                constant_type=protocol.get_type("Integer"),
                                constant_value=self.value
                            )
                        )
                    ]
                )
            )
        return output
