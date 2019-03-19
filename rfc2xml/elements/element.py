from lxml import etree
from typing import List, Dict, Union, Callable, Optional, Any
from ..xmlable import Xmlable


class Element(Xmlable):
    tag_name: str = None
    children: List[Union['Element', str]] = None

    def __init__(self):
        self.children = []

    def __str__(self):
        return self.to_xml_string(pretty=True)

    def to_xml(self):
        element = etree.Element(str(self.tag_name), self.get_attributes())
        self.children_to_xml(element)
        return element

    def to_xml_string(self, pretty=False):
        return etree.tostring(self.to_xml(), pretty_print=pretty).decode()

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
                if isinstance(child, list):
                    for c in child:
                        prev = c.to_xml()
                        element.append(prev)
                else:
                    prev = child.to_xml()
                    element.append(prev)

        return element

    def get_attributes(self) -> Dict[str, str]:
        return {}

    def get_str(self):
        o = ""
        for child in self.children:
            if isinstance(child, str):
                o += child
        return o

    def traverse(self, func: Callable[['Element', Any], Optional['Element']], update: bool = False, *args, **kwargs):
        """
        Traverses every element in the dom recursively. Will call function func on every element
        :param func: Callable function func(Element, *args, **kwargs)
        :param update: Whether elements should be updated
        :param args: Arguments passed to func
        :param kwargs: Keyword arguments passed to func
        :return: A new list of children
        """
        children = []
        for child in self.children:
            child = func(child, *args, **kwargs)
            if child is None:
                continue
            if isinstance(child, list):
                for c in child:
                    result = c.traverse(func, update, *args, **kwargs)
                    if update:
                        c.children = result
                        children.append(c)
            elif isinstance(child, Element):
                result = child.traverse(func, update, *args, **kwargs)
                if update:
                    child.children = result
                    children.append(child)
            else:
                if update:
                    children.append(child)
        if not update:
            return None
        return children

    def get_child_types(self, square_brackets: bool = False):
        """
        This function helps with debugging structures in the DOM. It generates a string that represents this structure
        :param square_brackets: Used internally by function only
        :return: String representing structure
        """
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
