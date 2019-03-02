from .elements import SectionStruct
from rfc2xml.elements import Rfc, Artwork, T, Figure, List as ListElement, Element
from rfc2xml.elements.section import Section
from .parse import Parse
from typing import Dict, Tuple, List, Optional, Union
from .elements import Field, FieldRef, ArtField
from protocol import Protocol, StructField, Expression
from .rel_loc import RelLoc
from input_parsers.extended_diagrams.elements.art import Art
from .names import Names
from input_parsers.extended_diagrams.exception import InvalidStructureException
from ometa.runtime import ParseError
from protocol import MethodInvocationExpression, FieldAccessExpression, ThisExpression, ConstantExpression,\
                     ArgumentExpression


class ExtendedDiagrams:
    dom: Rfc

    def __init__(self, filename: str):
        self.protocol = Protocol()
        self.dom = Parse.parse_file(filename)
        self.struct_lookup = {}
        self.struct_lookup_number = {}
        self.struct_names = []

    @staticmethod
    def section(section: Section, protocol: Protocol) -> Union[Section, List[SectionStruct]]:
        parse = Parse(protocol)

        # Get the indexes of the items in this section we care about
        try:
            ids = ExtendedDiagrams.section_to_structure_ids(section)
        except InvalidStructureException:
            return section

        # Return section without processing if no art was found
        if ids[1] == 0:
            return section

        intro = ExtendedDiagrams.section_intro(section, ids, parse)
        arts = ExtendedDiagrams.section_art(section, ids, parse)
        fields, refs = ExtendedDiagrams.section_fields(section, ids, parse)
        refs += ExtendedDiagrams.section_fields_post(section, ids, parse)

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

            section_struct = SectionStruct.from_section(intro, section, fields_new)

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
                    if field.name == Names.field_name_formatter(ref.field_loc):
                        fields.insert(
                            i + ref.rel_loc,
                            FieldRef(
                                name=ref.field_new,
                                constraint_value=ref.value,
                                constraint_field=ref.field_this,
                                section_number=ref.section_number,
                                optional=ref.optional
                            )
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
        return tuple(o)

    @staticmethod
    def section_intro(section: Section, ids: Tuple, parse: Parse) -> Optional[str]:
        if ids[0] == 0:
            return None

        intro = "\n".join(list(map(lambda a: a.get_str(), section.children[:ids[0]])))

        try:
            return parse.parser(intro).packet_intro()
        except ParseError:
            return None

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

            # If this field should be ignored, do that
            if "ignore" in attributes and attributes["ignore"]:
                continue

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
                except (AttributeError, IndexError):
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
    def section_fields_post(section: Section, ids: Tuple, parse: Parse):
        index = ids[0] + ids[1] + ids[2] + ids[3]
        text = "\n".join(list(map(lambda a: a.get_str(), section.children[index:])))
        try:
            return [parse.parser(text).fields_post()]
        except ParseError:
            return []

    @staticmethod
    def art_ids_to_fields_start_index(ids: Tuple):
        return ids[0]+ids[1]+ids[2]

    @staticmethod
    def art_start_index_and_ids_to_fields_end_index(start_index: int, ids: Tuple):
        return start_index+ids[3]

    def traverse_dom(self):
        self.dom.middle.children = self.dom.middle.traverse(
            lambda element:
                ExtendedDiagrams.section(element, self.protocol) if isinstance(element, Section) else element,
            update=True
        )

    ########################################################################################################
    # Protocol
    ########################################################################################################

    protocol: Protocol
    struct_names: List[str]
    struct_lookup: Dict[str, List[SectionStruct]]
    struct_lookup_number: Dict[str, List[SectionStruct]]

    def protocol_get_structs(self, child: Element):
        if isinstance(child, SectionStruct):
            if child.name not in self.struct_names:
                self.struct_names.append(child.name)
            if child.name not in self.struct_lookup:
                self.struct_lookup[child.name] = []
            if child.number not in self.struct_lookup_number:
                self.struct_lookup_number[child.number] = []
            self.struct_lookup[child.name].append(child)
            self.struct_lookup_number[child.number].append(child)
        return child

    def protocol_struct(self, struct: SectionStruct):
        name: str = struct.name
        fields: List[StructField] = []
        constraints: List[Expression] = []
        actions: List[Expression] = []

        for field in struct.children:
            if isinstance(field, FieldRef):

                # If this reference only exists if a value is set, construct that constraint
                is_present = None
                if field.constraint_value is not None:
                    is_present = MethodInvocationExpression(
                        method_name="eq",
                        target=FieldAccessExpression(
                            target=ThisExpression(),
                            field_name=field.constraint_field
                        ),
                        arg_exprs=[
                            ArgumentExpression(
                                "other",
                                ConstantExpression(
                                    constant_type=self.protocol.get_type("Integer"),
                                    constant_value=field.constraint_value
                                )
                            )
                        ]
                    )

                if field.section_number not in self.struct_lookup_number:
                    raise Exception("Section " + field.section_number + " referenced but this section can't be found")

                structs = self.struct_lookup_number[field.section_number]

                if not len(structs) == 1:
                    raise Exception(
                        "Section " + field.section_number + " but an unsupported number of structs was found"
                    )

                struct = structs[0]

                # If struct doesn't exist yet, create a temporary one
                if not self.protocol.is_type(struct.name):
                    field_type = self.protocol.define_struct(struct.name, [], [], [])
                else:
                    field_type = self.protocol.get_type(struct.name)

                fields.append(StructField(
                    field_name=struct.name,
                    field_type=field_type,
                    is_present=is_present,
                    transform=None
                ))

            elif isinstance(field, Field):

                # If a type is defined, use it
                if field.type is not None:
                    type_name = field.type + "$" + str(field.width)
                    if self.protocol.is_type(type_name):
                        field_type = self.protocol.get_type(type_name)
                    else:
                        field_type = self.protocol.define_bitstring(
                            name=type_name,
                            size=field.width
                        )

                # Otherwise create and use a generic type
                else:
                    # Find a unique generic type name for this field
                    type_name = "G$" + field.name + "$" + str(field.width)
                    i = 2
                    while self.protocol.is_type(type_name):
                        type_name = "G$" + field.name + "_" + str(i) + "$" + str(field.width)
                        i += 1

                    # Define this new type
                    field_type = self.protocol.define_bitstring(
                        name=type_name,
                        size=field.width
                    )

                fields.append(StructField(
                    field_name=field.name,
                    field_type=field_type,
                    is_present=None,
                    transform=None
                ))

                constraints += field.to_protocol_expressions()

        self.protocol.define_struct(name, fields, constraints, actions)

        if struct.pdu:
            self.protocol.define_pdu(name)

    def protocol_setup(self):
        self.protocol.set_protocol_name(Names.field_name_formatter(self.dom.front.title.get_str()))
        self.dom.middle.traverse(self.protocol_get_structs)
        for name in self.struct_lookup:
            structs = self.struct_lookup[name]
            if len(structs) == 1:
                self.protocol_struct(structs[0])
            else:
                raise Exception("Multiple structs in a struct not implemented")
        return self.protocol
