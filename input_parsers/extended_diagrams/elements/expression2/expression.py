from rfc2xml.elements import Element
from protocol import Expression as ProtocolExpression, Protocol


class Expression(Element):
    tag_name: str = "expression"

    def to_protocol_expression(self, protocol: Protocol):
        raise Exception("Not Implemented for class " + str(self.__class__))
