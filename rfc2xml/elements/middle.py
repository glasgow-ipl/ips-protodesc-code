from lxml import etree
from typing import List
from . import Element
from .section import Section


class Middle(Element):
    tag_name: str = "middle"
    children: List['Section'] = []

    def __init__(self):
        super().__init__()

    def add_section(self, section: 'Section'):
        self.children.append(section)
