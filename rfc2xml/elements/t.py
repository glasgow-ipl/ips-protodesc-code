from . import Element
from typing import List, Union, Dict


class T(Element):
    tag_name: str = "t"
    hang_text: str = None

    def __init__(self, children: List[Union['Element', str]] = None, hang_text: str = None):
        super().__init__()
        if children is None:
            children = []
        self.children = children
        self.hang_text = hang_text

    def get_attributes(self) -> Dict[str, str]:
        attributes = {}
        if self.hang_text is not None:
            attributes["hangText"] = self.hang_text
        return attributes

    def __str__(self):
        return str(self.children)
