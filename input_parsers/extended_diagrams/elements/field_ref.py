from rfc2xml.elements import Element


class FieldRef(Element):
    tag_name: str = "field_ref"
    name: str = None
    section_number: str = None
    constraint_value: int = None
    constraint_field: str = None
    optional: bool = False

    def __init__(self, name: str = None, section_number: str = None, constraint_value: int = None,
                 constraint_field: str = None, optional: bool = False):
        super().__init__()
        self.name = name
        self.section_number = section_number
        self.constraint_value = constraint_value
        self.constraint_field = constraint_field
        self.optional = optional

    def get_attributes(self):
        attributes = {}
        if self.name is not None:
            attributes["name"] = self.name
        if self.section_number is not None:
            attributes["section_number"] = self.section_number
        if self.constraint_value is not None:
            attributes["constraint_value"] = str(self.constraint_value)
        if self.constraint_field is not None:
            attributes["constraint_field"] = str(self.constraint_field)
        if self.optional:
            attributes["optional"] = str(self.optional)
        return attributes
