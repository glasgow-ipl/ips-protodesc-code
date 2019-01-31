from lxml import etree
from . import Element
from .organization import Organization


class Author(Element):
    tag_name: str = "author"
    initials: str = None
    surname: str = None
    organization: 'Organization' = None
    role: str = None

    def __init__(self, initials: str = None, surname: str = None, organization: 'Organization' = None, role: str = None):
        super().__init__()
        self.initials = initials
        self.surname = surname
        self.organization = organization
        self.role = role

    def get_attributes(self):
        attributes = {}
        if self.initials is not None:
            attributes["initials"] = self.initials
        if self.surname is not None:
            attributes["surname"] = self.surname
        if self.role is not None:
            attributes["role"] = self.role
        return attributes

    def to_xml(self):
        element = etree.Element(str(self.tag_name), self.get_attributes())
        if self.organization is not None:
            element.append(self.organization.to_xml())
        self.children_to_xml(element)
        return element
