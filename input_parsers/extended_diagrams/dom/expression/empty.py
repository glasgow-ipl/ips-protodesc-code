from . import Expression


class Empty(Expression):

    def to_dict(self):
        return None
