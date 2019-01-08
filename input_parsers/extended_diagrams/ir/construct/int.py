from . import NewType
from input_parsers.extended_diagrams.ir.trait import Trait


class Int(NewType):
    name = "Int"
    width = 32
    implements = [
        Trait("Ordinal"),
        Trait("ArithmeticOps")
    ]

    def __init__(self, width: int = 32):
        self.width = width
