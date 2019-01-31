from . import Element


class Organization(Element):
    tag_name: str = "organization"

    def __init__(self, value: str = None):
        super().__init__()
        self.children.append(value)
