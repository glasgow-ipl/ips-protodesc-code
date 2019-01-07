from . import NewType
from ..trait import Trait


class Int(NewType):
    name = "Int"
    width = 32
    derivedFrom = "BitString"
    implements = [
        Trait("Ordinal"),
        Trait("ArithmeticOps")
    ]

    def __init__(self, width: int = 32):
        self.width = width
