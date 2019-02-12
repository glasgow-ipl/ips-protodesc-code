import re
from rfc2xml.elements import Element, Section
from typing import List
from .field import Field


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
        new_section.name = new_section.format_name(section.title)
        new_section.number = section.number
        if fields is not None:
            for field in fields:
                field.name = new_section.new_name(field.name)
            new_section.children = fields
        new_section.children += section.get_sections()
        return new_section

    @staticmethod
    def format_name(name: str):
        name = name.lower()
        name = re.sub(r'[^.a-zA-Z0-9]', "_", name)
        while name.count("__") > 0:
            name = name.replace("__", "_")
        name = name.strip("_")
        return name

    def new_name(self, n):
        n = self.format_name(n)
        i = 2
        name = n
        while name in self.namespace:
            name = n + "$" + str(i)
            i = i + 1
        self.namespace.append(name)
        return name
