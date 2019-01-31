from lxml import etree
from typing import List, Union
from . import *
from .title import Title
from .date import Date
from .author import Author
from .workgroup import Workgroup
from .abstract import Abstract
from .note import Note


class Front(Element):
    tag_name: str = "front"
    title: 'Title' = None
    authors: List['Author'] = []
    date: 'Date' = None
    workgroup: 'Workgroup' = None
    abstract: 'Abstract' = Abstract()
    notes: List['Note'] = []

    def set_title(self, title: str):
        if self.title is None:
            self.title = Title(title)

    def set_date(self, date: 'Date' = None):
        self.date = date

    def add_note(self, title: str, children: List[Union['Element', str]]):
        self.notes.append(Note(title=title, children=children))

    def to_xml(self):
        element = etree.Element(str(self.tag_name), self.get_attributes())
        if self.title is not None:
            element.append(self.title.to_xml())
        for author in self.authors:
            element.append(author.to_xml())
        if self.date is not None:
            element.append(self.date.to_xml())
        if self.workgroup is not None:
            element.append(self.workgroup.to_xml())
        if self.abstract is not None:
            element.append(self.abstract.to_xml())
        if self.notes is not None:
            for note in self.notes:
                element.append(note.to_xml())
        self.children_to_xml(element)
        return element
