#!/usr/bin/env python3
import sys
import parsley
import string
import json
import itertools
import os
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from shared import *

#######################################################################
# Parsing
#######################################################################


def section_header(data, section_number, separator, title):
    l = section_number + separator + title + '\n'
    data['sections'][section_number] = l
    data['current_section'] = section_number
    return l


def section_regular(data, lines):
    if data["current_section"] is not None:
        data["sections"][data["current_section"]] += "".join(lines)
    return lines


def section_packet(data, packet, lines):
    section_regular(data, lines)
    for i in range(0, len(packet["pdus"])):
        if packet["pdus"][i]["section"] is None:
            packet["pdus"][i]["section"] = data["current_section"]
    data["packets"].append(packet)
    return packet


def get_data_section(data, section_number):
    try:
        section = data["sections"][section_number]
    except KeyError:
        raise Exception("Section '" + section_number + "' not found")
    return section.split("\n", 1)[1]


def unique_field_name(fields, fieldname):
    flag = False
    i = 1
    for field in fields:
        if field["name"] == fieldname:
            flag = True
        elif '$' in field["name"]:
            pos = field["name"].find("$")
            if field["name"][:pos] == fieldname:
                j = int(field["name"][pos+1:])
                if j > i:
                    i = j + 1
    if flag:
        return fieldname + "$" + str(i)
    else:
        return fieldname


def rfc(type_namespace, grammar, data):
    parser = get_parser(type_namespace, grammar, data=data)
    packets = []
    for packet in data["packets"]:
        type_namespace.clear()
        pdus = []
        for pdu in packet["pdus"]:
            section = get_data_section(data, pdu["section"])

            fields, where, types = parser(section).pdu()

            for type in types:
                type_name = type["name"]
                type_section = get_data_section(data, type["section"])

                type_fields, type_where, type_types = parser(type_section).structure()

                if len(type_types) > 0:
                    raise NotImplementedError("Section cannot reference a section that references another section")

                new_struct(type_name, type_fields, type_where, type_namespace, [], [])

            new_struct(pdu["title"], fields, where, type_namespace, [], [])
            pdus.append((pdu["title"], None))

        new_enum("PDUs", pdus, type_namespace)
        protocol = new_protocol(packet["title"], type_namespace)
        packets.append(protocol)

    return packets


def art_field(body, variable=False, name=None, value=None, array=None, width=None):

    o = {}

    if name is None:
        o["name"] = body.strip()
    else:
        o["name"] = str(name).strip()

    if value is not None:
        o["value"] = value

    if width:
        o["width"] = width
    elif variable:
        o["width"] = None
    else:
        o["width"] = round((len(body)+1)/2)

    if array:
        o["array"] = True

    return o


def art_field_binary(binary):
    return {
        "name": None,
        "value": int(binary, 2),
        "width": len(binary)
    }


def art_body(l):
    return list(itertools.chain.from_iterable(l))


def art_line(fields, last_field):
    if isinstance(last_field, dict):
        fields.append(last_field)
    return fields


def field_name_to_id(x):
    if x is None:
        return ""
    x = x.lower()
    x = re.sub('[^0-9a-z]+', '_', x)
    return x.strip('_')


def field_id_to_type_id(xs):
    o = ""
    for x in xs.split("_"):
        o += x.capitalize()
    return o


def string_to_type_id(xs):
    o = ""
    xs = re.sub('[^0-9a-zA-X]+', ' ', xs)
    for x in xs.split(" "):
        o += x.capitalize()
    return o


def fields(x):
    o = []
    for field in x:
        if isinstance(field, (list,)):
            o += field
        else:
            o.append(field)
    return o


#######################################################################
# IR Representation
#######################################################################


def new_generic_named_bitstring(type_namespace, name, size):
    type_name = name + "$"
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


def new_generic_bitstring(type_namespace, size):
    """
    Creates a generic bitstring for a given length
    :param type_namespace:
    :param size:
    :return:
    """
    return new_generic_named_bitstring(type_namespace, "BitString", size)


def get_generic_name(type_namespace, type):
    max = -1
    for key in type_namespace:
        if key[0:7] == type+"$" and key[7:].isnumeric():
            val = int(key[7:])
            if val > max:
                max = val
    if max == -1:
        return type+"$1"
    return type+"$" + str(max + 1)


def where_value(field_name, value, type_namespace):
    start = build_accessor_chain({"expression": "This"}, [field_name])
    pairs = [["==", build_integer_expression(value, type_namespace)]]
    return build_tree(start, pairs, "")


def new_field_name(field_order, new_names, name):
    """
    Creates a new unique field name
    :param field_order: The order of the existing fields (list of names)
    :param new_names: The new names added this session (list of names)
    :param name: Given name (might not be unique)
    :return:
    """
    names = field_order + new_names
    i = 2
    while name in names:
        name = name + "_" + str(i)
        i = i + 1
    return name


def new_structures_field_location_init(new_structs, section):
    if section not in new_structs:
        new_structs[section] = []


def new_structures_append(new_structs, location, section, name):
    new_structs[section].append({
        "location": location,
        "structure_section": section,
        "name": name
    })


def fields_to_new_structures(field_order, field_attributes):
    new_structs = {}
    new_names = []
    for field_id in field_order:
        field = field_attributes[field_id]
        structure_location = field.get("structure_location")
        if structure_location:
            section_number = field["structure_location"]["field_location"]

            new_structures_field_location_init(new_structs, section_number)

            if field["structure_location"]["relative_location"] == "precede":
                location = -1
            elif field["structure_location"]["relative_location"] == "follow":
                location = 1
            else:
                raise Exception("Expected 'precede' or 'follow', got " + field["structure_location"]["relative_location"])

            name = new_field_name(field_order, new_names, field["structure_location"]["field_new"])
            new_names.append(name)

            new_structures_append(new_structs, location, section_number, name)

        structure_section = field.get("structure_section")
        if structure_section:
            section_number = field["structure_section"]
            new_structures_field_location_init(new_structs, section_number)
            new_structures_append(new_structs, 0, section_number, field_id)

    return new_structs


def field_new_fields_location(structures, field_attributes, field_id, location):
    """
    Get any new fields that should be inserted either before, instead
    of, or after the current field. Location: -1=Before, 0=Instead,
    1=After
    :param structures:
    :param field_attributes:
    :param field_id:
    :param location:
    :return:
    """
    o = []
    if field_id in structures:
        for struct in structures[field_id]:
            if struct["location"] == location:
                o.append(struct["name"])
                field_attributes[struct["name"]] = {
                    "structure_section": struct["structure_section"]
                }
    if location == 0 and len(o) == 0:
        o.append(field_id)
    return o


def field_new_fields(structures, field_attributes, field_id):
    """
    Get any new fields that should be inserted before, instead of, or
    after the current field
    :param structures:
    :param field_attributes:
    :param field_id:
    :return:
    """
    o = []
    o += field_new_fields_location(structures, field_attributes, field_id, -1)
    o += field_new_fields_location(structures, field_attributes, field_id, 0)
    o += field_new_fields_location(structures, field_attributes, field_id, 1)
    return o


def new_structures_to_fields(structures, field_order, field_attributes):
    o = []
    for field_id in field_order:
        o += field_new_fields(structures, field_attributes, field_id)
    return o, field_attributes


def structure(type_namespace, data, art, fields):
    field_order, field_attributes = structure_fields(art, fields)
    structures = fields_to_new_structures(field_order, field_attributes)
    field_order, field_attributes = new_structures_to_fields(structures, field_order, field_attributes)

    fields = []
    where = []
    types = []

    for field_id in field_order:
        field = field_attributes[field_id]

        # If this field is a structure defined elsewhere
        if "structure_section" in field:


            type_name = string_to_type_id(field_id)

            fields.append(new_field_data(field_id, type_name))
            types.append({
                "name": type_name,
                "section": field["structure_section"]
            })
            continue

        if "type" in field and field["type"] is not None:
            type_name = string_to_type_id(field["type"])
            type_name = new_generic_named_bitstring(type_namespace, type_name, field['width'])

        else:
            type_name = new_generic_bitstring(type_namespace, field['width'])

        fields.append(new_field(field_id, (type_name, None), None, type_namespace))

        if "value" in field:
            where.append(where_value(field_id, field["value"], type_namespace))

        if "constraint" in field:
            start = build_accessor_chain({"expression": "This"}, [field_id, "length"])
            pairs = [["==", build_integer_expression(field["constraint"], type_namespace)]]
            where.append(build_tree(start, pairs, ""))

    return fields, where, types


def pdu(type_namespace, data, art, fields):
    return structure(type_namespace, data, art, fields)


def merge_value(v1, v2):
    """
    Takes two values and returns the one to use in the merge. Used by
    dictionary merge.
    :param v1:
    :param v2:
    :return:
    """
    if v2 is None:
        return v1
    if v1 is None:
        return v2
    if v1 != v2:
        raise ValueError(
            "Two different values found. Don't know which one to use")
    return v1


def merge(d1, d2):
    """
    Merge two dictionaries together.
    :param d1:
    :param d2:
    :return:
    """

    d2_keys = list(d2.keys())
    for key in d1.keys():
        if key in d2_keys:
            try:
                d1[key] = merge_value(d1[key], d2[key])
            except ValueError:
                raise ValueError(
                    "Two different values found for key '" + key + "'. "
                    "Don't know which one to use")
            d2_keys.remove(key)
    for key in d2_keys:
        d1[key] = d2[key]
    return d1


def structure_fields(art, fields):
    """
    Takes in data extracted from the ASCII art diagram and the field
    text and generates a structure based on this
    :param art:
    :param fields:
    :return:
    """

    field_order = []
    field_attributes = {}

    # Process all fields that were in the art work
    static_id = 1
    for a in art:
        id = field_name_to_id(a['name'])

        # If this is a static field (I.e. it has no name)
        if id == "":
            id = "Static$" + str(static_id)
            static_id = static_id + 1

        a.pop('name', None)
        field_order.append(id)
        field_attributes[id] = a

    for f in fields:
        id = f['id']

        if f['abbrv'] is not None:
            id_abbrv = field_name_to_id(f['abbrv'])

            # If the abbreviation exists as a key
            if id_abbrv in field_attributes:

                # Change abbreviation to full field name
                field_attributes[id] = field_attributes.pop(id_abbrv)
                field_order[field_order.index(id_abbrv)] = id

            # Otherwise, if the id isn't in field_attributes throw error
            elif id not in field_attributes:
                raise SyntaxError("Item '" + f['name'] + "' in field list was not found in the ascii diagram")

        # Remove keys that are either redundant or too verbose
        f.pop('description', None)
        f.pop('id', None)
        f.pop('abbrv', None)
        f.pop('name', None)

        if id not in field_attributes:
            raise SyntaxError(
                "Field '" + id + "' in field list was not found "
                "in the ascii diagram")

        try:
            field_attributes[id] = merge(field_attributes[id], f)
        except ValueError:
            raise SyntaxError(
                "Field '" + id + "' has contradictory information"
                " in field list and ASCII diagram. Don't know which to"
                " believe"
            )

    return field_order, field_attributes

#######################################################################
# Main
#######################################################################


def get_parser_file(type_namespace, filename="extended_diagrams.txt", data=None):
    with open(filename) as fp:
        grammar = fp.read()
    return get_parser(type_namespace, grammar, data=None)


def get_parser(type_namespace, grammar, data=None):

    if data is None:
        data = {
            "current_section": None,
            "sections": {},
            "packets": [],
        }

    return parsley.makeGrammar(grammar, {
        'punctuation': string.punctuation,
        'section_header': section_header,
        'section_regular': section_regular,
        'section_packet': section_packet,
        'rfc': rfc,
        'art_field': art_field,
        'art_field_binary': art_field_binary,
        'art_body': art_body,
        'art_line': art_line,
        'field_name_to_id': field_name_to_id,
        'structure': structure,
        'pdu': pdu,
        'fields': fields,

        'grammar': grammar,

        'type_namespace': type_namespace,
        'bitstrings': [],

        'build_integer_expression': build_integer_expression,
        'build_tree': build_tree,
        'build_accessor_chain': build_accessor_chain,

        'data': data
    })


def parse_file(filename):
    with open(filename) as fp:
        contents = fp.read()

    type_namespace = {}
    parser = get_parser_file(
        type_namespace,
        filename=os.path.dirname(os.path.realpath(__file__)) + "/extended_diagrams.txt"
    )
    return parser(contents).rfc()


def main():
    o = parse_file(sys.argv[1])
    print(json.dumps(o, indent=4))



if __name__ == "__main__":
    main()