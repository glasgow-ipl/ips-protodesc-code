from . import Element


class Date(Element):
    tag_name: str = "date"

    year: int = None
    month: str = None
    day: int = None

    def get_attributes(self):
        attributes = {}
        if self.year is not None:
            attributes["year"] = self.year
        if self.month is not None:
            attributes["month"] = self.month
        if self.day is not None:
            attributes["day"] = self.day
        return attributes

    def __init__(self, year: int = None, month: str = None, day: int = None):
        super().__init__()
        self.year = year
        self.month = month
        self.day = day

    def __str__(self):
        if None not in (self.year, self.month, self.day):
            return str(self.month) + " " + str(self.day) + ", " + str(self.year)
        output = ""
        if self.month is not None:
            output += str(self.month) + " "
        if self.day is not None:
            output += str(self.day) + " "
        if self.year is not None:
            output += str(self.year) + " "
        return output.strip()
