from . import Element
from typing import Dict


class Title(Element):
    tag_name: str = "title"
    abbrev: str = None

    def __init__(self, value: str = None):
        super().__init__()
        if value is not None:
            self.children.append(value)

    def get_attributes(self) -> Dict[str, str]:
        attributes = {}
        if self.abbrev is not None:
            attributes["abbrev"] = self.abbrev

        return attributes
