from shared import *
from typing import List, Dict, Tuple
import re
import json
from .dom.element.art import Art
from .dom.element.field import Field
from .dom.element.fields import Fields
from .dom.section.section import Section
from .dom.expression import FieldAccess, Constant, Expression
from .dom.expression.method_invocation import Eq


class ExtendedDiagrams:

    @staticmethod
    def new_generic_named_bitstring(type_namespace, name, size):
        type_name = str(name) + "$"
        if size is None:
            type_name += "None"
            bits = None
        elif size < 0:
            type_name += "Variable"
            bits = None
        else:
            type_name += str(size)
            bits = ('Bits', size)

        if type_name not in type_namespace:
            new_bitstring(type_name, bits, type_namespace)
        return type_name

    @staticmethod
    def new_generic_bitstring(type_namespace, size):
        """
        Creates a generic bitstring for a given length
        :param type_namespace:
        :param size:
        :return:
        """
        return ExtendedDiagrams.new_generic_named_bitstring(
            type_namespace, "BitString", size
        )

    @staticmethod
    def string_to_field_id(x):
        if x is None:
            return ""
        x = x.lower()
        x = re.sub('[^0-9a-z]+', '_', x)
        return x.strip('_')

    @staticmethod
    def string_to_type_id(xs):
        o = ""
        xs = re.sub('[^0-9a-zA-Z]+', ' ', xs)
        for x in xs.split(" "):
            o += x.capitalize()
        return o

    def pdu_section(self, section: Section, type_namespace: Dict) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        names = []
        for element in section.elements:
            names.append(element.get_name())

        if names != ['Art', 'Fields']:
            raise Exception("PDU does not have the correct elements")

        pdu_fields, where = self.pdu(section.elements[0], section.elements[1])

        fields = []
        definitions = []
        for field in pdu_fields:
            field_id = self.string_to_field_id(field.name)
            if field.type is None:
                type_name = self.new_generic_bitstring(type_namespace, field.width)
            else:
                type_name = self.new_generic_named_bitstring(type_namespace, field.type, field.width)
            fields.append(new_field(field_id, (type_name, None), None, type_namespace))

            if field.expressions is not None:
                where += Expression.list_to_dict(field.expressions)
                definitions += field.get_definitions_dict()

        return fields, where, definitions

    @staticmethod
    def process_field(field: 'Field', items: Dict, order: List):
        if field.abbrv in items:
            items[field.name] = items.pop(field.abbrv)
            items[field.name].name = field.name
            order[order.index(field.abbrv)] = field.name

        if field.name in items:
            items[field.name].merge(field)

        else:
            raise Exception(
                "Item in field list that is not in ASCII diagram"
            )

    @staticmethod
    def pdu(art: Art, fields: Fields) -> Tuple[List['Field'], List[Dict]]:
        order = []
        items = {}
        where = []

        static_index = 1
        for field in art.fields:
            if field.name is None:
                field.name = "Static$" + str(static_index)

                expression = Eq(
                    Constant(field.value),
                    [FieldAccess(field.name)]
                )

                where.append(expression.to_dict())

                static_index += 1

            order.append(field.name)
            items[field.name] = field.to_field()

        for field in fields.fields:
            if isinstance(field, (list,)):
                for f in field:
                    ExtendedDiagrams.process_field(f, items, order)
            else:
                ExtendedDiagrams.process_field(field, items, order)

        output = []
        for name in order:
            output.append(items[name])

        return output, where

    @staticmethod
    def rfc(dom):
        self = ExtendedDiagrams()

        type_namespace = {}
        pdus = []

        for section in dom.sections:
            if section.type == "pdu":
                fields, where, definitions_section = self.pdu_section(section, type_namespace)

                for definition in definitions_section:

                    # If this item has already been defined
                    if definition["name"] in type_namespace:
                        if type_namespace[definition["name"]] is not definition:
                            raise Exception(definition["name"] + " has been defined elsewhere")

                    # Otherwise, add it to the type namespace
                    else:
                        type_namespace[definition["name"]] = definition

                title = self.string_to_type_id(section.title)

                new_struct(title, fields, where, type_namespace, [], [])
                pdus.append((title, None))

        new_enum("PDUs", pdus, type_namespace)
        return new_protocol("TODO Protocol Name", type_namespace)
