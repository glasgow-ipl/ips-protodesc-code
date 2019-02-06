from . import Element
from typing import List as TypingList, Union, Dict


class List(Element):
    tag_name: str = "list"
    style: str = None

    def __init__(self, children: TypingList[Union['Element', str]] = None, style: str = None):
        super().__init__()
        if children is None:
            children = []
        self.children = children
        self.style = style

    def __str__(self):
        return str(self.children)

    def get_attributes(self) -> Dict[str, str]:
        attributes = {}
        if self.style is not None:
            attributes["style"] = self.style
        return attributes
