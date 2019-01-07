from . import Construct


class NewType(Construct):
    name = None
    width = None
    derivedFrom = None
    implements = []

    def to_dict(self):
        implements = []
        for implement in self.implements:
            implements.append(implement.to_dict())

        return {
            "construct": "NewType",
            "name": str(self.name) + "$" + str(self.width),
            "derived_from": str(self.derivedFrom) + "$" + str(self.width),
            "implements": implements
        }
