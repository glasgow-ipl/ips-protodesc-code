from . import Expression
from protocol import ThisExpression, Protocol


class This(Expression):
    tag_name: str = "expression_this"

    def to_protocol_expression(self, protocol: Protocol):
        return ThisExpression()
