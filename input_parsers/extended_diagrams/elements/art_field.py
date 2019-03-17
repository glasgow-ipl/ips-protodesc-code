from rfc2xml.elements import Element


class ArtField(Element):
    tag_name: str = "art_field"
    name = None
    width = None
    value = None
    array = None
    abbrv = None

    def __init__(self, name: str=None, width: int=None, value: int=None,
                 array: bool=None, abbrv: str=None):
        super().__init__()
        self.name = name
        self.width = width
        self.value = value
        self.array = array
        self.abbrv = abbrv

    def parse(self, body: str = None, variable: bool = False,
              name: str = None, value: int = None, array: bool = None,
              width: int = None, abbrv: str = None):

        if body is None:
            body = ""

        if name is None:
            self.name = body.strip()
        else:
            self.name = str(name).strip()

        if value is not None:
            self.value = value

        if width:
            self.width = width
        elif variable:
            self.width = None
        else:
            self.width = round((len(body) + 1) / 2)

        if array:
            self.array = True

        self.abbrv = abbrv

        return self

    def to_field(self):
        from .field import Field
        from .field_array import FieldArray

        field = Field(
            name=self.name,
            width=self.width,
            value=self.value,
            abbrv=self.abbrv
        )

        if self.array:
            return FieldArray.from_field(field)

        return field

    def get_attributes(self):
        attributes = {}
        if self.name is not None:
            attributes["name"] = self.name
        if self.width is not None:
            attributes["width"] = str(self.width)
        if self.value is not None:
            attributes["value"] = str(self.value)
        if self.array is not None:
            attributes["array"] = str(self.array)
        if self.abbrv is not None:
            attributes["abbrv"] = str(self.abbrv)
        return attributes
