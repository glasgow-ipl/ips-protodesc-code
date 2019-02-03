from typing import List
from . import *


class Fields(Element):
    fields = []

    def __init__(self, fields: List['Field'] = None):
        if fields is None:
            fields = []
        self.fields = fields

    def new_field(self, field: 'Field'):
        self.fields.append(field)

    def to_dict(self):
        fields = []
        for f in self.fields:
            if isinstance(f, (list,)):
                for f2 in f:
                    fields.append(f2.to_dict())
            else:
                fields.append(f.to_dict())

        return {
            **super(Fields, self).to_dict(),
            "attributes": {
                "fields": fields,
            }
        }

    def __repr__(self):
        return str(self.to_dict())