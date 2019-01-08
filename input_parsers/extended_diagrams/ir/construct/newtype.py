from . import Construct
from . import BitString


class NewType(Construct):
    name = None
    width = None
    implements = []

    def get_derived(self) -> Construct:
        return BitString(width=self.width)

    def to_dict(self):
        derived = self.get_derived()

        implements = []
        for implement in self.implements:
            implements.append(implement.to_dict())

        return [
            derived.to_dict(),
            {
                "construct": "NewType",
                "name": str(self.name) + "$" + str(self.width),
                "derived_from": derived.get_name(),
                "implements": implements
            }
        ]
