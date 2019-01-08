class Trait:
    name = None

    def __init__(self, name=None):
        self.name = name

    def to_dict(self):
        return {
            "trait": self.name
        }