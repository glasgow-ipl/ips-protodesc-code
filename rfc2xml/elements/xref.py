from . import Element


class Xref(Element):
    tag_name: str = "xref"
    target: str = None

    def __init__(self, target: str = None):
        super().__init__()
        self.target = target

    def get_attributes(self):
        attributes = {}
        if self.target is not None:
            attributes["target"] = self.target
        return attributes
