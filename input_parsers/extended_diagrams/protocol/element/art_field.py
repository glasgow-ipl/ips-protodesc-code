from .element import Element


class ArtField(Element):
    name = None
    width = None
    value = None
    array = None
    abbrv = None

    def __init__(self, name: str=None, width: int=None, value: int=None,
                 array: bool=None, abbrv: str=None):
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

    def to_dict(self):
        return {
            **super(ArtField, self).to_dict(),
            "attributes": self.__dict__
        }

    def to_field(self):
        from ...elements.field import Field
        return Field(
            name=self.name,
            width=self.width,
            value=self.value,
            array=self.array,
            abbrv=self.abbrv
        )

    def __repr__(self):
        return str(self.to_dict())
