from typing import List
from ..element import Element


class Section:
    number = None
    title = None
    type = None
    elements = []

    def __init__(self, number: str, title: str, type: str = None, elements: List['Element'] = None) -> None:
        if elements is None:
            elements = []

        self.number = number
        self.title = title
        self.type = type
        self.elements = elements

    def new_element(self, element: 'Element'):
        self.elements.append(element)

    def to_dict(self):
        elements = []
        for e in self.elements:
            elements.append(e.to_dict())

        return {
            "type": "Section",
            "attributes": {
                "number": self.number,
                "title": self.title,
                "type": self.type,
                "elements": elements
            }
        }

    def __repr__(self):
        return str(self.to_dict())