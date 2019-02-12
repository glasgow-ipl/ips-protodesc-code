from . import Expression


class Constant(Expression):
    tag_name: str = "expression_constant"
    value: int = None
    size: int = 32

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
