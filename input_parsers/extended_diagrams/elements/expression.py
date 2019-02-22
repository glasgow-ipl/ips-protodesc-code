from rfc2xml.elements import Element
from protocol import Expression as ProtocolExpression
from lxml import etree


class Expression(Element):
    tag_name: str = "expression"
    expression: ProtocolExpression

    def __init__(self, expression: ProtocolExpression):
        super().__init__()
        self.expression = expression

    def get_expression_text(self) -> str:
        return str(self.expression.__class__)

    def to_xml(self):
        element = etree.Element(str(self.tag_name), self.get_attributes())
        element.text = etree.CDATA("\n" + self.get_expression_text() + "\n")
        return element
