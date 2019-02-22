from . import Expression
from protocol import ConstantExpression, BitString, Protocol


class Constant(Expression):
    tag_name: str = "expression_constant"
    value: int = None
    size: int = 4

    def __init__(self, value=None):
        super().__init__()
        self.value = value

    def get_attributes(self):
        attributes = super().get_attributes()
        if self.value is not None:
            attributes["value"] = str(self.value)
        if self.size is not None:
            attributes["size"] = str(self.size)
        return attributes

    def to_protocol_expression(self, protocol: Protocol):
        type = BitString(
            name="BitString$" + str(self.size),
            size=self.size
        )
        type.implement_trait(protocol.get_trait("Sized"))
        type.implement_trait(protocol.get_trait("Value"))
        type.implement_trait(protocol.get_trait("Equality"))

        return ConstantExpression(
            constant_type=type,
            constant_value=self.value
        )
