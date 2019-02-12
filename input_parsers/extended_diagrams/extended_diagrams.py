import sys
import re
from .elements import SectionStruct
from rfc2xml.elements import Rfc, Artwork, T
from rfc2xml.elements.section import Section
from ometa.runtime import ParseError
from .parse import Parse
from typing import Dict, Tuple
from .elements import Field, FieldRef
from protocol import Protocol
from .rel_loc import RelLoc


class ExtendedDiagrams:
    dom: Rfc

    def __init__(self, filename: str):
        self.dom = Parse.parse_file(filename)

    @staticmethod
    def section(section: Section, args: Dict = None):
        #if args is None or "extended_diagrams" not in args:
        #    raise Exception("self not passed to section")
        #self = args["extended_diagrams"]s

        parse = Parse()

        child_types = section.get_child_types()

        # TODO: Replace with representation that doesn't convert to string to parse
        # Get the indexes of the items in this section we care about
        try:
            ids = parse.parser(child_types).dom_structure()
        except ParseError:
            return section

        #art = ExtendedDiagrams.section_art(section, ids, parse)
        fields = ExtendedDiagrams.section_fields(section, ids, parse)

        return SectionStruct.from_section(section, fields)

    @staticmethod
    def strip_double_underscore(s: str):
        while s.count("__") > 0:
            s = s.replace("__", "_")
        return s

    @staticmethod
    def type_name_formatter(name: str):
        name = re.sub(r'[^.a-zA-Z0-9]', "_", name)
        while name.count("__") > 0:
            name = name.replace("__", "_")
        name = name.strip("_")
        name = name[0].upper() + name[1:]
        return name

    @staticmethod
    def section_art(section: Section, ids: Tuple, parse: Parse):
        """
        Get art from a section and parse it
        :param section:
        :param ids:
        :param parse:
        :return:
        """

        art = []
        for i in range(0, ids[1]):
            figure = section.children[ids[0] + i]
            if len(figure.children) <= 0:
                raise Exception("Figure doesn't have enough children\n\n" + figure.__str__())
            artwork = figure.children[0]
            if not isinstance(artwork, Artwork):
                raise Exception("Figure does not contain expected artwork\n\n" + artwork.__str__())
            art.append(parse.parser(artwork.text).packet_artwork())
        return art

    @staticmethod
    def section_fields(section: Section, ids: Tuple, parse: Parse):
        """
        Get text fields from a section and parse it
        :param section:
        :param ids:
        :param parse:
        :return:
        """
        start_index = ExtendedDiagrams.art_ids_to_fields_start_index(ids)
        end_index = ExtendedDiagrams.art_start_index_and_ids_to_fields_end_index(start_index, ids)

        fields = []
        refs = []

        for i in range(start_index, end_index, 2):
            (field, attributes) = parse.parser(section.children[i].get_str()).field_title(Field())

            # If field is a list of control bits
            if "control" in attributes and attributes["control"]:
                try:
                    text = section.children[i + 1].children[0].children[0].children[0]
                except IndexError:
                    raise Exception("Control structure did not contain expected structure")
                fields += parse.parser(text).field_control()
                continue

            else:

                # Get the array of paragraph objects
                try:
                    ts = section.children[i+1].children[0].children
                except IndexError:
                    raise Exception("Field item body did not contain expected structure")

                # Get array of text for every paragraph in field description
                paragraphs = []
                for t in ts:
                    paragraphs.append(t.get_str())

                # Get single piece of text representing description
                text = "\n".join(paragraphs)

                refs += parse.parser(text).field_body()
                fields.append(field)

        for ref in refs:
            if isinstance(ref, RelLoc):
                for i in range(0, len(fields)):
                    field = fields[i]
                    if field.name == ref.field_loc:
                        fields.insert(
                            i + ref.rel_loc,
                            FieldRef(name=ref.field_new, value=ref.value, section_number=ref.section_number)
                        )
                        break

        return fields

    @staticmethod
    def art_ids_to_fields_start_index(ids: Tuple):
        return ids[0]+ids[1]+ids[2]

    @staticmethod
    def art_start_index_and_ids_to_fields_end_index(start_index: int, ids: Tuple):
        return start_index+ids[3]

    def traverse_dom(self):
        self.dom.middle.children = self.dom.middle.traverse_sections(ExtendedDiagrams.section, {"extended_diagrams": self})

    def protocol(self):
        protocol = Protocol()
        protocol.set_protocol_name(ExtendedDiagrams.type_name_formatter(self.dom.front.title.get_str()))

        struct = protocol.define_struct("AAAAABBBBBBBCCCCCCCCC")

        return protocol
