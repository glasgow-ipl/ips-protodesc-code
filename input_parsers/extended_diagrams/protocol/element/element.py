from ...dictionarable import Dictionarable


class Element(Dictionarable):

    def get_name(self):
        return self.__class__.__name__

    def to_dict(self):
        return {
            "type": self.get_name()
        }
