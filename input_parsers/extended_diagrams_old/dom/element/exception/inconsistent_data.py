class InconsistentData(Exception):
    field = None
    attribute = None
    value1 = None
    value2 = None

    def __init__(self, message, field=None, attribute=None, value1=None, value2=None):
        self.field = field
        self.attribute = attribute
        self.value1 = value1
        self.value2 = value2
        self.update_message()

    def update(self, field=None, attribute=None, value1=None, value2=None):
        if field is not None:
            self.field = field
        if attribute is not None:
            self.attribute = attribute
        if value1 is not None:
            self.value1 = value1
        if value2 is not None:
            self.value2 = value2
        self.update_message()
        return self

    def get_message(self) -> str:
        o = ""
        if self.field:
            o += "'" + str(self.field) + "' "
        if self.attribute:
            o += "'" + str(self.attribute) + "' is "
        if self.value1:
            o += "'" + str(self.value1) + "'"
        if self.value1 and self.value2:
            o += " and "
        if self.value2:
            o += "'" + str(self.value2) + "'"
        return o

    def update_message(self):
        super().__init__(self.get_message())