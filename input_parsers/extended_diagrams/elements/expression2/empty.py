from . import Expression
from protocol import Protocol


class Empty(Expression):
    tag_name: str = "expression_empty"

    def to_protocol_expression(self, protocol: Protocol):
        return None
