from . import Construct


class BitString(Construct):
    name = None
    width = None

    def __init__(self, name: str = None, width: int = None):
        self.name = name
        self.width = width

    def get_name(self):
        if self.name is None:
            return self.get_generic_name()
        return self.name

    def get_generic_name(self) -> str:
        return self.__class__.__name__ + "$" + str(self.width)

    def to_dict(self):
        return {
            **super(BitString, self).to_dict(),
            "name": self.get_generic_name(),
            "width": self.width
        }
