from typing import List
from rfc2xml.elements import Element
from .art_field import ArtField


class Art(Element):
    tag_name: str = "art"
    fields = []

    def __init__(self, fields: List['ArtField'] = None):
        super().__init__()
        if fields is None:
            fields = []

        self.fields = fields

    def new_field(self, field: 'ArtField'):
        self.fields.append(field)

    def children_to_xml(self, element):
        for child in self.fields:
            element.append(child)
