from . import Element


class Workgroup(Element):
    tag_name: str = "workgroup"

    def __init__(self, value: str = None):
        super().__init__()
        if value is not None:
            self.children.append(value)
