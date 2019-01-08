from . import Expression


class This(Expression):

    @staticmethod
    def to_dict():
        return {
            "expression": "This"
        }
