from . import Expression
from protocol import ThisExpression


class This(Expression):
    tag_name: str = "expression_this"

    def to_protocol_expression(self):
        return ThisExpression()
