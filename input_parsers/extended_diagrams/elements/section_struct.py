import re
from rfc2xml.elements import Element, Section
from typing import List
from .field import Field
from input_parsers.extended_diagrams.names import Names


class SectionStruct(Section):
    tag_name: str = "section_struct"
    name: str = None
    namespace: List[str] = None

    def __init__(self):
        super().__init__()
        self.namespace = []

    def get_attributes(self):
        attributes = super().get_attributes()
        if self.name is not None:
            attributes["name"] = self.name
        return attributes

    @staticmethod
    def from_section(section: 'Section', fields: List['Field'] = None) -> 'SectionStruct':
        new_section = SectionStruct()
        new_section.name = Names.field_name_formatter(section.title)
        new_section.number = section.number
        if fields is not None:
            for field in fields:
                field.name = new_section.new_name(field.name)
            new_section.children = fields
        new_section.children += section.get_sections()
        return new_section

    def new_name(self, n):
        n = Names.field_name_formatter(n)
        i = 2
        name = n
        while name in self.namespace:
            name = n + "$" + str(i)
            i = i + 1
        self.namespace.append(name)
        return name
