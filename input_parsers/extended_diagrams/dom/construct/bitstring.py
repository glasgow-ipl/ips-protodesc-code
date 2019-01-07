from . import Construct


class BitString(Construct):
    name = None
    width = None

    def to_dict(self):
        return {
            **super(BitString, self).to_dict(),
            "name": self.name,
            "width": self.width
        }