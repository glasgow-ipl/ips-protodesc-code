from typing import List
from .section import Section


class Middle(Section):
    tag_name: str = "middle"
    children: List['Section'] = []

    def __init__(self):
        super().__init__()

    def add_section(self, section: 'Section'):
        self.children.append(section)
