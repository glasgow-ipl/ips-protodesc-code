import parsley
import string
import os
import sys
import itertools
from typing import List as TypingList, Tuple, Union
from . import Rfc
from .elements import Date, Author, Organization, Workgroup, Xref, T, TocItem, Section, List, Figure, Artwork


class Rfc2Xml:

    @staticmethod
    def get_parser_file(filename):
        with open(filename) as fp:
            grammar = fp.read()
        return Rfc2Xml.get_parser(grammar)

    @staticmethod
    def get_parser(grammar):
        return parsley.makeGrammar(grammar, {
            'punctuation': string.punctuation,
            'ascii_uppercase': string.ascii_uppercase,
            'ascii_lowercase': string.ascii_lowercase,
            'itertools': itertools,
            'ExtendedDiagrams': Rfc2Xml,

            'rfc': Rfc(compliant=True),

            'Date': Date,
            'Xref': Xref,
            'TocItem': TocItem,
            'Section': Section,
            'List': List,
            'Figure': Figure,
            'Artwork': Artwork,
            'T': T,

            'rfc_title_docname': Rfc2Xml.rfc_title_docname,
            'rfc_title_abbrev': Rfc2Xml.rfc_title_abbrev,
            'front_names': Rfc2Xml.front_names,
            'text_paragraph': Rfc2Xml.text_paragraph,
            'sections': Rfc2Xml.sections,
            'printr': Rfc2Xml.printr
        })

    @staticmethod
    def parse_file(filename) -> 'Rfc':
        with open(filename) as fp:
            contents = fp.read()
        return Rfc2Xml.parse(contents)

    @staticmethod
    def parse(string):
        string += "\n\n"  # TODO this is a hacky solution to the grammar requiring a double new line end of file
        parser = Rfc2Xml.get_parser_file(
            filename=os.path.dirname(os.path.realpath(__file__)) + "/grammar.txt"
        )
        return parser(string).rfc()

    @staticmethod
    def rfc_title_docname(rfc: 'Rfc', title: str, docname: str):
        if not docname:
            docname = None
        rfc.docname = docname
        rfc.front.set_title(title)

    @staticmethod
    def rfc_title_abbrev(rfc: 'Rfc', abbrev: str):
        if rfc.front.title.abbrev is None:
            rfc.front.title.abbrev = abbrev

    @staticmethod
    def front_names(rfc: 'Rfc', data: TypingList[Tuple]):
        left, right = zip(*data)
        names = []

        for item in right:
            if item is None:
                continue
            if item["type"] == "name":
                names.append(item)
            elif item["type"] == "organization":
                organization = Organization(item["name"])
                for name in names:
                    author = Author(
                        initials=name["initials"],
                        surname=name["surname"],
                        organization=organization,
                        role=Rfc2Xml.suffix_to_role(name["role"])
                    )
                    rfc.front.authors.append(author)
                names = []

            else:
                raise Exception("Invalid item type ", item["type"])

        rfc.front.workgroup = Workgroup(left[0])

        # TODO: Don't throw away data such as Intended status and Expires

    @staticmethod
    def suffix_to_role(suffix: str):
        if suffix is None:
            return None
        suffix = suffix.lower()
        if suffix == "ed":
            return "editor"
        else:
            print("Warning: Found unknown author suffix ", suffix, file=sys.stderr)
            return suffix

    @staticmethod
    def text_paragraph(arr: TypingList[Union[str, Xref]], hang_text: str = None):
        # Format array of strings and objects so that a list of strings and objects is produced where sequential
        # strings are concatenated
        o = [arr[0]]
        for a in arr[1:]:
            if isinstance(a, str):
                if isinstance(o[-1], str):
                    o[-1] += a
                else:
                    o.append(a)
            else:
                o.append(a)

        return T(children=o, hang_text=hang_text)

    @staticmethod
    def sections(arr: TypingList[Section]):
        out = []
        current = []
        current_level = None

        for a in reversed(arr):
            split = a.number.split(".")
            level = len(split) - 1

            if current_level is None:
                current_level = level

            if level > current_level:
                out = current + out
                current = []
                current_level = level

            if level == current_level:
                current.insert(0, a)
            elif level < current_level:
                a.children += current
                current = [a]
                current_level = level

        return current + out

    @staticmethod
    def printr(x, v=None):
        print(str(x))
        if v is None:
            return x
        else:
            return v
