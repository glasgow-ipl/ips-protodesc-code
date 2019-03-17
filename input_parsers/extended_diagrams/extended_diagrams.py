from typing import Dict, Tuple, List, Optional, Union
from ometa.runtime import ParseError
from protocol import Protocol
from rfc2xml import Rfc2Xml
from rfc2xml.elements import Rfc, Artwork, T, Figure, List as ListElement
from rfc2xml.elements.section import Section
from .elements import SectionStruct, Field, FieldRef, ArtField, FieldArray, Art
from .names import Names
from .parse import Parse
from .rel_loc import RelLoc
from .exception import InvalidStructureException


class ExtendedDiagrams:
    dom: Rfc
    protocol: Protocol

    def __init__(self) -> None:
        super().__init__()
        self.protocol = Protocol()

    def load_dom(self, filename: str) -> None:
        """
        Loads DOM by parsing input file
        :param filename: input filename
        :return: None
        """
        self.dom = Rfc2Xml.parse_file(filename)

    def traverse_dom(self) -> None:
        """
        Traverse DOM to update to protocol specific DOM
        :return: None
        """
        self.dom.middle.children = self.dom.middle.traverse(
            lambda element: self._section(element) if isinstance(element, Section) else element,
            update=True
        )

    def setup_protocol(self) -> Protocol:
        """
        Setup protocol from current DOM
        :return: None
        """
        from . import ExtendedDiagramsProtocol
        return ExtendedDiagramsProtocol.setup(self.dom, self.protocol)

    def _section(self, section: Section) -> Union[Section, List[SectionStruct]]:
        """
        Update DOM section to protocol specific section if this is a structure
        :param section: DOM section
        :return: The original section or the new structure section
        """

        # Load parser
        parse = Parse(self.protocol)

        # If this is a structure, get indexes (for locating elements within this section). Otherwise, return the old
        # section.
        try:
            ids = self._section_to_structure_ids(section)
        except InvalidStructureException:
            return section

        # Return section without processing if no art was found
        if ids[1] == 0:
            return section

        intro = self._section_intro(section, ids, parse)
        arts = self._section_art(section, ids, parse)
        fields, refs, arrays = self._section_fields(section, ids, parse)
        ref, field_descriptions = self._section_fields_post(section, ids, parse)

        if ref is not None:
            refs.append(ref)

        output = []
        for art in arts:

            # Convert art into lookup dict and order list
            lookup, order = self._art_to_lookup_order(art)

            # Update lookup with details from field
            for field in fields:
                self._field_update_from_lookup(field, lookup, order)

            # Update fields with details from artwork
            fields_new = self._lookup_order_to_fields(lookup, order)

            self._fields_process_refs(refs, fields_new)

            section_struct = SectionStruct.from_section(intro, section, fields_new, field_descriptions)

            output.append(section_struct)

        return output

    @staticmethod
    def _section_intro(section: Section, ids: Tuple, parse: Parse) -> Optional[str]:
        """
        Parse the section intro to get the packet name (if it exists)
        :param section: The section
        :param ids: Indexes (for locating elements within this section)
        :param parse: Parser
        :return: Packet name (if it exists)
        """

        # If no items are in the intro, return None
        if ids[0] == 0:
            return None

        # Get all of the intro paragraphs as one string
        intro = "\n".join(list(map(lambda a: a.get_str(), section.children[:ids[0]])))

        # Parse packet intro to get the packet name, if failure return None
        try:
            return parse.parser(intro).packet_intro()
        except ParseError:
            return None

    @staticmethod
    def _section_art(section: Section, ids: Tuple, parse: Parse) -> List[Art]:
        """
        Get art from a section and parse it
        :param section: The section
        :param ids: Indexes (for locating elements within this section)
        :param parse: Parser
        :return: List of art DOM elements
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

    def _section_fields(self, section: Section, ids: Tuple, parse: Parse) -> Tuple[List[Field], List[RelLoc], List[Dict]]:
        """
        Get text fields from a section and parse it
        :param section: The section
        :param ids: Indexes (for locating elements within this section)
        :param parse: Parser
        :return: fields, refs, arrays
        """
        start_index = self._art_ids_to_fields_start_index(ids)
        end_index = self._art_start_index_and_ids_to_fields_end_index(start_index, ids)

        fields = []
        refs = []
        arrays = []

        # For each pair of elements (i.e. each field)
        for i in range(start_index, end_index, 2):

            # Parse field title line for attributes
            try:
                (field, attributes) = parse.parser(section.children[i].get_str()).field_title(Field())
            except ParseError:
                continue

            # If this field should be ignored, do that
            if "ignore" in attributes and attributes["ignore"]:
                pass

            # If field is a list of control bits
            elif "control" in attributes and attributes["control"]:
                self._section_fields_control(section, parse, fields, i)

            # Otherwise, this is a regular field
            else:
                self._section_fields_regular(section, parse, field, fields, refs, arrays, i)

        return fields, refs, arrays

    @staticmethod
    def _section_fields_control(section: Section, parse: Parse, fields: List[Field], i: int) -> None:
        """
        Parse field body for a selection of control bits
        :param section: The section
        :param parse: Parser
        :param fields: The output list of fields
        :param i: The field index
        :return:
        """
        try:
            text = section.children[i + 1].children[0].children[0].children[0]
        except IndexError:
            raise Exception("Control structure did not contain expected structure")
        fields += parse.parser(text).field_control()

    @staticmethod
    def _section_fields_regular(section: Section, parse: Parse, field: Field, fields: List[Field], refs: List[RelLoc],
                                arrays: List[Dict], i: int) -> None:
        """
        Parse field body for a regular field
        :param section: The section
        :param parse: Parser
        :param field: The current field
        :param fields: The output list of fields
        :param refs: The output list of references
        :param arrays: The output list of arrays
        :param i: The field index
        :return:
        """

        # Get the array of paragraph objects
        try:
            ts = section.children[i + 1].children[0].children
        except (AttributeError, IndexError):
            raise Exception("Field item body did not contain expected structure")

        # Get array of text for every paragraph in field description
        paragraphs = []
        for t in ts:
            paragraphs.append(t.get_str())

        # Get single piece of text representing description
        text = "\n".join(paragraphs)

        body_type, body_contents = parse.parser(text).field_body(field)

        if body_type == "refs":
            refs += body_contents

        elif body_type == "array":
            field = FieldArray.from_field(field, body_contents["section_number"])
            arrays += body_contents

        # DEBUG print
        elif body_type == "print":
            print(body_contents)

        fields.append(field)

    def _section_fields_post(self, section: Section, ids: Tuple, parse: Parse) -> Tuple[Optional[RelLoc], Optional[str]]:
        """
        Get post fields elements and parse them to get extra references
        :param section: The section
        :param ids: Indexes (for locating elements within this section)
        :param parse: The parser
        :return:
        """
        index = self._art_ids_to_post_fields_start_index(ids)
        text = "\n".join(list(map(lambda a: a.get_str(), section.children[index:])))

        result = parse.parser(text).fields_post()

        return (
            None if "ref" not in result else result["ref"],
            None if "field_descriptions" not in result else result["field_descriptions"]
        )

    @staticmethod
    def _art_to_lookup_order(art: 'Art') -> Tuple[Dict[str, ArtField], List[str]]:
        """
        Convert art into lookup dict and order list
        :param art: The artwork
        :return: Dict for looking up an artwork element by name
                 List for representing the order of the fields
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
    def _field_update_from_lookup(field: 'Field', lookup: Dict, order: List[str]) -> None:
        """
        Update lookup with details from field
        :param field: The current field
        :param lookup: Dict for looking up an artwork element by name
        :param order: List for representing the order of the fields
        :return: None
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
    def _lookup_order_to_fields(lookup: Dict, order: list) -> List[Field]:
        """
        Update fields with details from artwork
        :param lookup: Dict for looking up an artwork element by name
        :param order: List for representing the order of the fields
        :return: List of fields
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
    def _fields_process_refs(refs: List[RelLoc], fields: List[Union[Field, FieldRef]]):
        """
        Process field references to update existing fields
        :param refs: References
        :param fields: Existing fields to update
        :return: None
        """
        for ref in refs:
            if isinstance(ref, RelLoc):
                for i in range(0, len(fields)):
                    field = fields[i]
                    if field.name == Names.field_name_formatter(ref.field_loc):

                        field_ref = FieldRef (
                            name=ref.field_new,
                            constraint_value=ref.value,
                            constraint_field=ref.field_this,
                            section_number=ref.section_number,
                            optional=ref.optional,
                            condition=ref.condition
                        )

                        # If this field should replace the current
                        if ref.rel_loc is None:
                            fields[i] = field_ref

                        else:
                            fields.insert(
                                i + ref.rel_loc,
                                field_ref
                            )
                        break

    @staticmethod
    def _art_ids_to_fields_start_index(ids: Tuple) -> int:
        """
        Gets the index of the first item in the fields list
        :param ids: Indexes (for locating elements within this section)
        :return: ID
        """
        return ids[0]+ids[1]+ids[2]

    @staticmethod
    def _art_start_index_and_ids_to_fields_end_index(start_index: int, ids: Tuple) -> int:
        """
        Gets the index of the last item in the fields list
        :param start_index: Start index of fields list (generated by _art_ids_to_fields_start_index)
        :param ids: Indexes (for locating elements within this section)
        :return: ID
        """
        return start_index+ids[3]

    @staticmethod
    def _art_ids_to_post_fields_start_index(ids: Tuple) -> int:
        """
        Gets the index of the first item in the post fields elements
        :param ids: Indexes (for locating elements within this section)
        :return: ID
        """
        return ids[0] + ids[1] + ids[2] + ids[3]

    @staticmethod
    def _section_to_structure_ids(section: Section):
        """
        Get indexes (for locating elements within this section) from a section
        :param section: The section
        :return: The indexes
        """
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
                if isinstance(section.children[j].children[0], ListElement):
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

            if j >= len(section.children)\
                    or\
                    (not isinstance(section.children[j], T)
                        or
                     not isinstance(section.children[j].children[0], ListElement)):
                j = j - 1
                break
            j = j + 1
        o[3] = j - i
        o[4] = len(section.children)-j

        # If no field list but post field contents exist, correct the IDs
        if o[2] > 0 and o[3] == 0 and o[4] == 0:
            o[4] = o[2]
            o[3] = 0
            o[2] = 0

        return tuple(o)
