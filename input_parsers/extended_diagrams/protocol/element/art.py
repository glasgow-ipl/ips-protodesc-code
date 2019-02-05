from typing import List
from .element import Element
from .art_field import ArtField


class Art(Element):
    fields = []

    def __init__(self, fields: List['ArtField'] = None):
        if fields is None:
            fields = []

        self.fields = fields

    def new_field(self, field: 'ArtField'):
        self.fields.append(field)

    def to_dict(self):
        fields = []
        for f in self.fields:
            fields.append(f.to_dict())

        return {
            **super(Art, self).to_dict(),
            "attributes": {
                "fields": fields,
            }
        }

    def __repr__(self):
        return str(self.to_dict())
