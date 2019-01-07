class Construct:

    def get_name(self):
        return self.__class__.__name__

    def to_dict(self):
        return {
            "construct": self.get_name()
        }
