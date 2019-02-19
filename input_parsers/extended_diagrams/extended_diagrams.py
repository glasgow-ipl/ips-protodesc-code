from .elements import SectionStruct
from rfc2xml.elements import Rfc, Artwork, T, Figure, List
from rfc2xml.elements.section import Section
from .parse import Parse
from typing import Dict, Tuple
from .elements import Field, FieldRef, ArtField
from protocol import Protocol
from .rel_loc import RelLoc
from input_parsers.extended_diagrams.elements.art import Art
from .names import Names
from input_parsers.extended_diagrams.exception import InvalidStructureException


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

        # Get the indexes of the items in this section we care about
        try:
            ids = ExtendedDiagrams.section_to_structure_ids(section)
        except InvalidStructureException as error:
            return section

        arts = ExtendedDiagrams.section_art(section, ids, parse)
        fields, refs = ExtendedDiagrams.section_fields(section, ids, parse)

        output = []
        for art in arts:

            # Convert art into lookup dict and order list
            lookup, order = ExtendedDiagrams.art_to_lookup_order(art)

            # Update lookup with details from field
            for field in fields:
                ExtendedDiagrams.field_update_from_lookup(field, lookup, order)

            # Update fields with details from artwork
            fields_new = ExtendedDiagrams.lookup_order_to_fields(lookup, order)

            ExtendedDiagrams.fields_process_refs(refs, fields_new)

            section_struct = SectionStruct.from_section(section, fields_new)

            output.append(section_struct)

        return output

    @staticmethod
    def art_to_lookup_order(art: 'Art'):
        """
        Convert art into lookup dict and order list
        :param art:
        :return:
        """
        lookup = {}
        order = []
        for a in art.fields:
            name = Names.field_name_formatter(a.name)
            a.name = name
            lookup[name] = a
            order.append(name)
        return lookup, order

    @staticmethod
    def field_update_from_lookup(field: 'Field', lookup: Dict, order: list):
        """
        Update lookup with details from field
        :param field:
        :param lookup:
        :param order:
        :return:
        """
        name = Names.field_name_formatter(field.name)
        abbrv = Names.field_name_formatter(field.abbrv)

        if name not in lookup:
            if abbrv in lookup:
                f = lookup.pop(abbrv)
                order[order.index(abbrv)] = name
                f.name = name
                lookup[name] = f
            else:
                raise Exception("Field '" + name + "' in field list not in ASCII diagram")
        field.name = name
        lookup[name] = lookup[name].to_field().merge(field)

    @staticmethod
    def lookup_order_to_fields(lookup: Dict, order: list):
        """
        Update fields with details from artwork
        :param lookup:
        :param order:
        :return:
        """
        fields = []
        for o in order:
            field = lookup[o]
            if isinstance(field, Field):
                fields.append(field)
            elif isinstance(field, ArtField):
                fields.append(field.to_field())
            else:
                raise Exception(
                    "Incorrect type of field found in field array. Found " + str(field.__class__) + "\n\n" + str(field)
                )
        return fields

    @staticmethod
    def fields_process_refs(refs: list, fields: list):
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

    @staticmethod
    def section_to_structure_ids(section: Section):
        o = [-1, -1, -1, -1, -1]

        i = j = 0
        while j < len(section.children):
            if isinstance(section.children[j], Figure):
                break
            elif not isinstance(section.children[j], T):
                raise InvalidStructureException("Start of section not structured T* Figure+")
            j = j + 1
        o[0] = j - i
        i = j

        while j < len(section.children):
            if isinstance(section.children[j], T):
                break
            elif not isinstance(section.children[j], Figure):
                raise InvalidStructureException("Start of section not structured T* Figure+ T")
            j = j + 1
        o[1] = j - i
        i = j

        while j < len(section.children):
            if isinstance(section.children[j], T):
                if isinstance(section.children[j].children[0], List):
                    j = j - 1
                    break
            else:
                raise InvalidStructureException("Start of section not structured T* Figure+ (T T[List])*")
            j = j + 1
        o[2] = j - i
        i = j

        while j < len(section.children):
            if not isinstance(section.children[j], T):
                break
            j = j + 1

            if j >= len(section.children) or (not isinstance(section.children[j], T) and not isinstance(section.children[j].children[0], List)):
                j = j - 1
                break
            j = j + 1
        o[3] = j - i
        o[4] = len(section.children)-j
        return tuple(o)

    @staticmethod
    def section_art(section: Section, ids: Tuple, parse: Parse) -> list:
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

        return fields, refs

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
        protocol.set_protocol_name(Names.type_name_formatter(self.dom.front.title.get_str()))

        struct = protocol.define_struct("AAAAABBBBBBBCCCCCCCCC")

        return protocol
