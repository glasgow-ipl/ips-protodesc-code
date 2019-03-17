from . import Field
from ..exception import InconsistentDataException


class FieldArray(Field):
    tag_name: str = "field_array"
    type_section: str = None

    @staticmethod
    def from_field(field: 'Field', type_section: str = None) -> 'FieldArray':
        field.__class__ = FieldArray
        if isinstance(field, FieldArray):
            field.type_section = type_section
            return field
        raise Exception("Could not convert Field to FieldArray")

    def get_attributes(self):
        attributes = super().get_attributes()
        if self.type_section is not None:
            attributes["type_section"] = self.type_section
        return attributes

    def merge(self, field: 'Field', ignore_value: bool = False) -> 'FieldArray':
        super().merge(field)
        if isinstance(field, FieldArray):
            try:
                self.merge_field(field, 'type_section')
            except InconsistentDataException as error:
                raise error.update(field=field.name)
        return self
