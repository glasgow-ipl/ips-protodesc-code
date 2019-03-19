from typing import List
from lxml import etree
from . import *
from .front import Front
from .middle import Middle
from .back import Back
from .toc import Toc
from .toc_item import TocItem


class Rfc(Element):
    tag_name: str = "rfc"

    # compliant with xml2rfc?
    compliant: bool = False

    docname: str = None
    toc: 'Toc' = None
    front: 'Front' = Front()
    middle: 'Middle' = Middle()
    back: 'Back' = Back()

    def __init__(self, compliant: bool = False):
        super().__init__()
        self.compliant = compliant

    def set_toc_children(self, children: List[TocItem]):
        if self.toc is None:
            self.toc = Toc()
        self.toc.children = children

    def get_attributes(self):
        attributes = {}
        if self.docname is not None:
            attributes["docName"] = self.docname
        return attributes

    def to_xml(self):
        element = etree.Element(str(self.tag_name), self.get_attributes())
        if not self.compliant and self.toc is not None:
            element.append(self.toc.to_xml())
        element.append(self.front.to_xml())
        element.append(self.middle.to_xml())
        self.children_to_xml(element)
        return element
