from . import Element
from typing import Union


class Figure(Element):
    tag_name: str = "figure"
    title: str = None

    def __init__(self, title: str = None, child: Union['Element', str] = None):
        super().__init__()
        self.title = title
        if child is not None:
            self.add_child(child)

    def get_attributes(self):
        attributes = {}
        if self.title is not None:
            attributes["title"] = self.title
        return attributes

    def __str__(self):
        o = ""
        for child in self.children:
            o += child.__str__()
        if self.title is not None:
            o += "\n\nFigure: " + str(self.title)
        return o
