from . import Element
from lxml import etree


class Artwork(Element):
    tag_name: str = "artwork"
    text: str = None

    def __init__(self, text: str = None):
        super().__init__()
        text = text.rstrip()

        lines = text.split("\n")
        ws = len(lines[0]) - len(lines[0].lstrip(' '))

        for l in lines[1:]:
            v = len(l) - len(l.lstrip(' '))
            if v < ws:
                ws = v

        self.text = ""
        for l in lines:
            self.text += l[ws:] + "\n"

    def to_xml(self):
        element = etree.Element(str(self.tag_name), self.get_attributes())
        if self.text is not None:
            element.text = etree.CDATA("\n" + self.text)
        return element

    def __str__(self):
        return self.text
