from typing import List
from .section.section import Section


class Dom:
    sections = []
    lookup = {}

    def __init__(self, sections: List['Section'] = None):
        if sections is None:
            sections = []

        for section in sections:
            self.new_section(section)

    def new_section(self, section: 'Section') -> None:
        """
        Add a new section to the document
        :param section:
        :return:
        """

        if section.number in self.lookup:
            raise Exception("Section number already exists")

        self.lookup[section.number] = len(self.sections)
        self.sections.append(section)

    def get_section(self, section_number: str) -> Section:
        """
        Get a section using its section number
        :param section_number:
        :return:
        """

        if section_number not in self.lookup:
            raise Exception("Section number does not exist")

        return self.sections[self.lookup[section_number]]

    def to_dict(self):
        sections = []
        for s in self.sections:
            sections.append(s.to_dict())

        return {
            "type": "Dom",
            "attributes": {
                "sections": sections,
            }
        }

    def __repr__(self):
        return str(self.to_dict())
