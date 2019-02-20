from . import Expression


class Empty(Expression):
    tag_name: str = "expression_empty"

    def to_protocol_expression(self):
        return None
