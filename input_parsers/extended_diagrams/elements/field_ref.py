from rfc2xml.elements import Element


class FieldRef(Element):
    tag_name: str = "field_ref"
    name: str = None
    section_number: str = None
    value: int = None

    def __init__(self, name: str = None, section_number: str = None, value: int = None):
        super().__init__()
        self.name = name
        self.section_number = section_number
        self.value = value

    def get_attributes(self):
        attributes = {}
        if self.name is not None:
            attributes["name"] = self.name
        if self.section_number is not None:
            attributes["section_number"] = self.section_number
        if self.value is not None:
            attributes["value"] = str(self.value)
        return attributes
