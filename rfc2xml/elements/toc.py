from typing import List
from . import Element
from .toc_item import TocItem


class Toc(Element):
    tag_name: str = "toc"
    children: List[TocItem] = []

    def __init__(self):
        super().__init__()
