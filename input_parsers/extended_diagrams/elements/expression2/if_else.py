from lxml import etree
from . import Expression, Empty
from protocol import IfElseExpression, Protocol


class IfElse(Expression):
    tag_name: str = "expression_if_else"
    condition: 'Expression'
    if_true: 'Expression'
    if_false: 'Expression'

    def __init__(self, condition: 'Expression' = None, if_true: 'Expression' = None, if_false: 'Expression' = None):
        super().__init__()
        if condition is None:
            condition = Empty()
        if if_true is None:
            if_true = Empty()
        if if_false is None:
            if_false = Empty()

        self.condition = condition
        self.if_true = if_true
        self.if_false = if_false

    def children_to_xml(self, element):
        condition = etree.Element("condition")
        condition.append(self.condition.to_xml())
        element.append(condition)
        if_true = etree.Element("if_true")
        if_true.append(self.if_true.to_xml())
        element.append(if_true)
        if_false = etree.Element("if_false")
        if_false.append(self.if_false.to_xml())
        element.append(if_false)

    def to_protocol_expression(self, protocol: Protocol):
        return IfElseExpression(
            condition=self.condition.to_protocol_expression(protocol),
            if_false=self.condition.to_protocol_expression(protocol),
            if_true=self.condition.to_protocol_expression(protocol)
        )
