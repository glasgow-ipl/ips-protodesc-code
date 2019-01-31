from . import Element


class TocItem(Element):
    tag_name: str = "toc_item"
    section: str = None
    title: str = None
    page: int = None

    def __init__(self, section: str = None, title: str = None, page: int = None):
        super().__init__()
        self.section = section
        self.title = title
        self.page = page

    def get_attributes(self):
        attributes = {}
        if self.section is not None:
            attributes["section"] = self.section
        if self.title is not None:
            attributes["title"] = self.title
        if self.page is not None:
            attributes["page"] = str(self.page)
        return attributes
