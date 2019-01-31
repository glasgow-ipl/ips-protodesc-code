from . import Element


class Section(Element):
    tag_name: str = "section"
    title: str = None
    number: str = None

    def __init__(self, title: str = None, number: str = None):
        super().__init__()
        self.title = title
        self.number = number

    def get_attributes(self):
        attributes = {}
        if self.title is not None:
            attributes["title"] = self.title
        if self.number is not None:
            attributes["number"] = self.number
        return attributes

    def __str__(self):
        return str(self.number) + ". " + str(self.title)

    def __repr__(self):
        return self.__str__()