class Construct:
    name = None

    def get_name(self) -> str:
        return str(self.name)

    def get_construct_name(self):
        return self.__class__.__name__

    def to_dict(self):
        return {
            "construct": self.get_construct_name()
        }
