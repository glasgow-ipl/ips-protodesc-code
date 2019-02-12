from lxml import etree
from typing import List, Dict, Union, Callable
from ..xmlable import Xmlable


class Element(Xmlable):
    tag_name: str = None
    children: List[Union['Element', str]] = None

    def __init__(self):
        self.children = []

    def __str__(self):
        return etree.tostring(self.to_xml(), pretty_print=True).decode()

    def to_xml(self):
        element = etree.Element(str(self.tag_name), self.get_attributes())
        self.children_to_xml(element)
        return element

    def set_children(self, children: List[Union['Element', str]] = None):
        self.children = children
        return self

    def add_child(self, child: Union['Element', str]):
        self.children.append(child)
        return self

    def prepend_child(self, child: Union['Element', str]):
        self.children = [child] + self.children
        return self

    def add_children(self, children: List[Union['Element', str]] = None):
        self.children += children
        return self

    def children_to_xml(self, element):
        prev = None
        for child in self.children:
            if isinstance(child, str):
                if prev is None:
                    if element.text is None:
                        element.text = child
                    else:
                        element.text += " " + child
                else:
                    if prev.tail is None:
                        prev.tail = child
                    else:
                        prev.tail += " " + child
            else:
                prev = child.to_xml()
                element.append(prev)

        return element

    def get_attributes(self) -> Dict[str, str]:
        return {}

    def get_child_types(self, square_brackets: bool = False):
        o = ""
        for i in range(0, len(self.children)):
            child = self.children[i]
            if not isinstance(child, str):
                o += child.__class__.__name__
                if isinstance(child, Element) and len(child.children) > 0:
                    o += child.get_child_types(True)
                o += ","
        if o == "":
            return ""
        return o if not square_brackets else "[" + o + "]"

    def get_str(self):
        o = ""
        for child in self.children:
            if isinstance(child, str):
                o += child
        return o
