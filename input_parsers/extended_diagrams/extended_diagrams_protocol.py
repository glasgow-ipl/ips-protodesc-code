import sys
from typing import Dict, List, Union, Tuple, Optional
from protocol import Protocol, StructField, Expression, MethodInvocationExpression, FieldAccessExpression,\
                     ThisExpression, ConstantExpression, ArgumentExpression
from rfc2xml.elements import Element, Rfc
from .elements import SectionStruct
from .exception import SectionReferenceNotFound
from .elements import Field, FieldRef, FieldArray
from .names import Names


class ExtendedDiagramsProtocol:

    # The protocol
    protocol: Protocol

    # List of all section struct names
    section_struct_names: List[str]

    # Dict to lookup a section struct by its name
    section_struct_lookup: Dict[str, List[SectionStruct]]

    # Dict to lookup a section struct by its section number
    section_struct_lookup_number: Dict[str, List[SectionStruct]]

    # Defined structs. List of Tuple (name, fields, constraints, actions)
    structs: List[Tuple[str, List[StructField], List[Expression], List[Expression]]]

    # PDUs
    pdus: List[str]

    # Whether a new generic type should be created for every field
    generic_type_per_field: bool = False

    def __init__(self, protocol: Protocol):
        self.protocol = protocol
        self.section_struct_lookup = {}
        self.section_struct_lookup_number = {}
        self.section_struct_names = []
        self.structs = []
        self.structs_used = []
        self.pdus = []

    @staticmethod
    def setup(dom: Rfc, protocol: Protocol) -> Protocol:
        """
        Setup a protocol from the DOM
        :param dom: Protocol specific DOM
        :param protocol: Current protocol object
        :return: Protocol
        """
        self = ExtendedDiagramsProtocol(protocol)
        self.protocol.set_protocol_name(Names.field_name_formatter(dom.front.title.get_str()))
        dom.middle.traverse(self._protocol_get_structs)
        for name in self.section_struct_lookup:
            structs = self.section_struct_lookup[name]
            if len(structs) == 1:
                self._protocol_struct(structs[0])
            else:
                raise Exception("Multiple structs in a struct not implemented")
        self._add_used_structs_and_pdus()
        return self.protocol

    def _protocol_get_structs(self, child: Element) -> Element:
        """
        Used to traverse the DOM. If we are at a SectionStruct, add details of it to class. Otherwise, just return
        the current element
        :param child: The current element
        :return: The current element
        """
        if isinstance(child, SectionStruct):
            if child.name not in self.section_struct_names:
                self.section_struct_names.append(child.name)
            if child.name not in self.section_struct_lookup:
                self.section_struct_lookup[child.name] = []
            if child.number not in self.section_struct_lookup_number:
                self.section_struct_lookup_number[child.number] = []
            self.section_struct_lookup[child.name].append(child)
            self.section_struct_lookup_number[child.number].append(child)
        return child

    def _protocol_struct(self, struct: SectionStruct) -> None:
        """
        Process a SectionStruct
        :param struct: The struct
        :return: None
        """

        # If field descriptions are found on a different section
        if struct.field_descriptions is not None:
            if struct.field_descriptions not in self.section_struct_lookup_number:
                raise SectionReferenceNotFound(struct.field_descriptions)
            structs_lookup = self.section_struct_lookup_number[struct.field_descriptions]
            if len(structs_lookup) != 1:
                raise Exception("Unexpected number of structs")
            struct_lookup = structs_lookup[0]

            # Update every item in the field with the imformation from the other section
            for field in struct.children:
                if isinstance(field, Field):
                    name = field.name.rstrip("$").lower()
                    for child in struct_lookup.children:
                        if isinstance(child, Field):
                            if (child.abbrv is not None and child.abbrv.lower() == name)\
                                    or \
                               (child.name is not None and child.name.lower() == name):
                                field.name = child.name
                                field.abbrv = child.abbrv
                                field.merge(child, ignore_value=True)
                                break

        name: str = struct.name
        fields: List[StructField] = []
        constraints: List[Expression] = []
        actions: List[Expression] = []

        # Loop through each SectionStruct child
        for field in struct.children:
            self._protocol_struct_field(fields, constraints, field)

        self.structs.append((name, fields, constraints, actions))

        if struct.pdu:
            self.pdus.append(name)

    def _protocol_struct_field(self, fields: List[StructField], constraints: List[Expression], field: Union[Element, str]):
        """
        Process a structure field
        :param fields:  The output list of fields
        :param constraints: The output list of constraints
        :param field: The element
        :return: None
        """

        # If this is a reference field
        if isinstance(field, FieldRef):
            fields.append(self._protocol_struct_field_ref(field))

        # If this is a reference field
        elif isinstance(field, FieldArray):
            fields.append(self._protocol_struct_field_array(field))
            constraints += field.to_protocol_expressions(self.protocol)

        # If this is a regular field
        elif isinstance(field, Field):
            fields.append(self._protocol_struct_field_regular(field))
            constraints += field.to_protocol_expressions(self.protocol)

    def _protocol_struct_field_ref(self, field: FieldRef) -> StructField:
        """
        Process a reference field in a struct
        :param field: The field
        :return: New StructField
        """

        # If this reference only exists if a value is set, construct that constraint
        is_present = None
        if field.condition is not None:
            is_present = field.condition.expression
        elif field.constraint_value is not None:
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

        if field.section_number not in self.section_struct_lookup_number:
            raise SectionReferenceNotFound(field.section_number)

        structs = self.section_struct_lookup_number[field.section_number]
        if not len(structs) == 1:
            raise Exception(
                "Section " + field.section_number + " had an unsupported number of structs was found"
            )
        struct = structs[0]

        # Get a unique type name
        field_name = self._unique_protocol_type_name(struct.name)
        self.structs_used.append(field_name)

        # Create a temporary structure
        field_type = self.protocol.define_struct(field_name, [], [], [])

        return StructField(
            field_name=struct.name,
            field_type=field_type,
            is_present=is_present,
            transform=None
        )

    def _protocol_struct_field_array(self, field: FieldArray) -> StructField:
        """
        Process an array field in a struct
        :param field: The field
        :return: New StructField
        """
        if field.type_section is None:

            # Define a new type for array elements
            element_type = self._new_generic_bitstring(field.name, field.width)

            # Define a new array
            array_name = self._unique_protocol_type_name(Names.type_name_formatter(field.name))
            array_type = self.protocol.define_array(array_name, element_type, None)

            return StructField(
                field_name=field.name,
                field_type=array_type,
                is_present=None,
                transform=None
            )

        else:
            if field.type_section not in self.section_struct_lookup_number:
                raise SectionReferenceNotFound(field.type_section)

            structs = self.section_struct_lookup_number[field.type_section]
            if not len(structs) == 1:
                raise Exception(
                    "Section " + field.type_section + " had an unsupported number of structs was found"
                )
            struct = structs[0]

            # Get a unique type name
            struct_name = self._unique_protocol_type_name(struct.name)
            self.structs_used.append(struct_name)

            # Create a temporary structure
            array_field_type = self.protocol.define_struct(struct_name, [], [], [])

            # Create a new array
            array_name = self._unique_protocol_type_name(Names.type_name_formatter(field.name))
            field_type = self.protocol.define_array(
                name=array_name,
                element_type=array_field_type,
                length=None
            )

            return StructField(
                field_name=struct.name,
                field_type=field_type,
                is_present=None,
                transform=None
            )

    def _protocol_struct_field_regular(self, field: Field) -> StructField:
        """
        Process a regular field in a struct
        :param field: The field
        :return: New StructField
        """
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
            field_type = self._new_generic_bitstring(field.name, field.width)

        return StructField(
            field_name=field.name,
            field_type=field_type,
            is_present=None,
            transform=None
        )

    def _unique_protocol_type_name(self, name: str):
        """
        Get a unique protocol type name
        :param name: Name to make unique
        :return: Name
        """
        output = name
        i = 2
        while self.protocol.is_type(output):
            output = name + "$" + str(i)
            i += 1
        return output

    def _add_used_structs_and_pdus(self):
        """
        Add used structs and pdus to protocol
        :return: None
        """
        for name, fields, constraints, actions in self.structs:
            if name in self.structs_used or name in self.pdus:
                self.protocol.define_struct(name, fields, constraints, actions)
        for pdu in self.pdus:
            self.protocol.define_pdu(pdu)

    def _new_generic_bitstring(self, name: str, width: Optional[int]):

        # If a new generic type should be created per field
        if self.generic_type_per_field:

            # Find a unique generic type name for this field
            type_name = "G$" + name + "$" + str(width)
            i = 2
            while self.protocol.is_type(type_name):
                type_name = "G$" + name + "_" + str(i) + "$" + str(width)
                i += 1

            # Define this new type
            return self.protocol.define_bitstring(
                name=type_name,
                size=width
            )

        # Otherwise, only add a new generic per width
        else:
            type_name = "BitString$" + str(width)
            if self.protocol.is_type(type_name):
                return self.protocol.get_type(type_name)
            else:
                return self.protocol.define_bitstring(
                    name=type_name,
                    size=width
                )
