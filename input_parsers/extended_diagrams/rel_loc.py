from protocol import Expression


class RelLoc:
    """
    Data class for storing details of a reference
    """

    field_this: str = None
    value: int = None
    field_new: str = None
    rel_loc: int = None
    field_loc: str = None
    section_number: str = None
    optional: bool = False
    condition: Expression = None

    def __init__(self, field_this: str = None, value: int = None, field_new: str = None, rel_loc: int = None,
                 field_loc: str = None, section_number: str = None, optional: bool = False,
                 condition: Expression = None) -> None:
        self.field_this = field_this
        self.value = value
        self.field_new = field_new
        self.rel_loc = rel_loc
        self.field_loc = field_loc
        self.section_number = section_number
        self.optional = optional
        self.condition = condition
