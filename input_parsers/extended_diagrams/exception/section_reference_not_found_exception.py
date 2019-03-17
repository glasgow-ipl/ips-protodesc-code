from typing import Optional


class SectionReferenceNotFound(Exception):

    def __init__(self, section: Optional[str] = None) -> None:
        if section is None:
            super().__init__("A section was referenced but this section can't be found")
        else:
            super().__init__("Section " + section + " referenced but this section can't be found")
