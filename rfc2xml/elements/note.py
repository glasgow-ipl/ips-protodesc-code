from . import Element
from typing import List, Union


class Note(Element):
    tag_name: str = "note"

    title: str = None

    def get_attributes(self):
        attributes = {}
        if self.title is not None:
            attributes["title"] = self.title
        return attributes

    def __init__(self, title: str = None, children: List[Union['Element', str]] = None):
        super().__init__()
        self.title = title
        if children is not None:
            self.children = children
