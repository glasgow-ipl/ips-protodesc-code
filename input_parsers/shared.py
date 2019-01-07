# =================================================================================================
# Copyright (C) 2018 University of Glasgow
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions 
# are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# SPDX-License-Identifier: BSD-2-Clause
# =================================================================================================

import re


def new_protocol(protocol_name, type_namespace):
    pdus = type_namespace["PDUs"]["variants"]
    type_namespace.pop("PDUs")
    return {"construct": "Protocol",
            "name": protocol_name,
            "definitions": [element for element in type_namespace.values()],
            "pdus": pdus}


def check_typename(name, type_namespace, should_be_defined):
    if name in type_namespace and not should_be_defined:
        raise Exception("Name '%s' has already been defined" % name)
    elif name not in type_namespace and should_be_defined:
        raise Exception("Name '%s' has not been defined" % name)
    return True


def new_bitstring(name, type_name, type_namespace):
    # if name is None, we'll generate one: don't want to check
    if name is not None:
        check_typename(name, type_namespace, False)

    # need to determine the width
    if type(type_name) is tuple:
        if type_name[1] is not None:
            width = type_name[1]
        else:
            width = 1
    else:
        width = None

    # generate a name if necessary
    if name is None:
        name = "BitString$" + str(width)

    # construct BitString
    bitstring = {"construct": "BitString", "name": name, "width": width}
    type_namespace[name] = bitstring
    return name


def new_array(name, type_name, type_namespace):
    length = type_name[1]
    type_name = type_name[0]

    # if name is None, we'll generate one: don't want to check
    if name is not None:
        check_typename(name, type_namespace, False)

    # check if built-in type, and create if needed
    if type(type_name) is tuple or type_name == "Bits":
        type_name = new_bitstring(None, type_name, type_namespace)

    # check if type has been defined
    check_typename(type_name, type_namespace, True)

    # generate a name if necessary
    if name is None:
        name = type_name + "$" + str(length)

	print("hello! %s" % type_name)

    if length == -1:
        length = None
        # construct Array
        array = {"construct": "Array", "name": name, "element_type": type_name, "length": length}
        type_namespace[name] = array
    elif length is not None:
        # construct Array
        array = {"construct": "Array", "name": name, "element_type": type_name, "length": length}
        type_namespace[name] = array
    else:
        derived_type = {"construct": "NewType", "name": name, "derived_from": type_name, "implements": []}
        type_namespace[name] = derived_type
    return name


def new_field(name, type_name, transform, type_namespace):
    length = type_name[1]
    type_name = type_name[0]

    check_typename(name, type_namespace, False)
    if type(type_name) is tuple or type_name == "Bits":
        type_name = new_bitstring(None, type_name, type_namespace)
    if length is not None:
        if length == -1:
            length = None
        type_name = new_array(None, (type_name, length), type_namespace)

    # check if type has been defined
    check_typename(type_name, type_namespace, True)

    # process transform
    if transform is not None and transform is tuple:
        to_typename = transform[1][0]
        to_length = transform[1][1]

        if type(to_typename) is tuple or to_typename == "Bits":
            to_typename = new_bitstring(None, to_typename, type_namespace)
        if to_length is not None:
            if to_length == -1:
                to_length = None
            to_typename = new_array(None, (to_typename, to_length), type_namespace)

        check_typename(to_typename, type_namespace, True)
        transform = {"into_name": transform[0], "into_type": to_typename, "using": None}

    is_present = True
    if transform is not None:
        is_present = transform
        transform = None

    return new_field_data(name, type_name, is_present, transform)


def new_field_data(name, type_name, is_present=True, transform=None):
    return {"name": name, "type": type_name, "is_present": is_present, "transform": transform}


def new_struct(name, fields, where_block, type_namespace, context, actions):
    check_typename(name, type_namespace, False)

    field_dict = {}
    transform_dict = {}
    # field processing
    for field in fields:
        assert field["name"] not in field_dict
        assert field["name"] not in context
        field_dict[field["name"]] = field
        if field["transform"] is not None:
            transform_dict[field["transform"]["into_name"]] = field["transform"]

    if name == "Context":
        assert where_block is None
        for field in fields:
            field.pop("is_present", None)
        context = {"construct": "Context", "fields": fields}
        type_namespace[name] = context
        return name

    # action processing
    if actions is None:
        actions = []

    for i in range(len(actions)):
        action = actions[i]
        # is the action transforming a field?
        if action["expression"] == "MethodInvocation" and action["method"] == "set" and action["self"][
            "expression"] == "FieldAccess":
            transform_dict[action["self"]["field_name"]]["using"] = action["arguments"]["value"]
            actions.pop(i)

    # construct Struct
    struct = {"construct": "Struct", "name": name, "fields": fields, "constraints": where_block, "actions": actions}
    type_namespace[name] = struct
    return name


def new_enum(name, variants, type_namespace):
    check_typename(name, type_namespace, False)

    checked_variants = []

    for variant in variants:
        type_name = variant[0]
        length = variant[1]
        if type(type_name) is tuple or type_name == "Bits":
            type_name = new_bitstring(None, type_name, type_namespace)
        if length is not None:
            if length == -1:
                length = None
            type_name = new_array(None, (type_name, length), type_namespace)
        if check_typename(type_name, type_namespace, True):
            checked_variants.append(type_name)

    # construct Enum
    enum = {"construct": "Enum", "name": name, "variants": [{"type": variant} for variant in checked_variants]}
    type_namespace[name] = enum
    return name


def new_func(name, params, ret_type, type_namespace):
    if len(params) > 1 and params[0] is None:
        raise Exception("Syntax error")
    check_typename(name, type_namespace, False)

    ret_type_name = ret_type[0]
    ret_length = ret_type[1]
    if type(ret_type_name) is tuple or ret_type_name == "Bits":
        ret_type_name = new_bitstring(None, ret_type_name, type_namespace)
    if ret_length is not None:
        if ret_length == -1:
            ret_length = None
        ret_type_name = new_array(None, (ret_type_name, ret_length), type_namespace)

    # construct Function
    function = {"construct": "Function", "name": name,
                "parameters": [param for param in params if param.pop('is_present', None)],
                "return_type": ret_type_name}
    type_namespace[name] = function
    return name


def new_func_call(name, args, type_namespace):
    if args[0] is None:
        args = []
    check_typename(name, type_namespace, True)
    def_args = type_namespace[name]["parameters"]
    def_args_names = [x["name"] for x in def_args]
    def_args_types = [x["type"] for x in def_args]
    named_args = [{"name": x[0], "value": x[1]} for x in zip(def_args_names, args)]
    return {"expression": "FunctionInvocation", "name": name, "arguments": named_args}


def build_integer_expression(num, type_namespace):
    # TODO: widths
    width = "32"
    int_typename = "Int$" + width
    if int_typename not in type_namespace:
        if "BitString$" + width not in type_namespace:
            new_bitstring(None, ("Bit", int(width)), type_namespace)
        type_namespace[int_typename] = {"construct": "NewType",
                                        "name": int_typename,
                                        "derived_from": "BitString$" + width,
                                        "implements": [{"trait": "Ordinal"},
                                                       {"trait": "ArithmeticOps"}]}
    return {"expression": "Constant", "type": int_typename, "value": num}


def build_accessor_chain(type, refs):
    if len(refs) != 1 and (refs[-1] == "length" or refs[-1] == "size" or refs[-1] == "width"):
        return {"expression": "MethodInvocation",
                "method": refs[-1],
                "self": build_accessor_chain(type, refs[:-1]) if len(refs) > 1 else type,
                "arguments": None}
    else:
        return {"expression": "FieldAccess",
                "target": build_accessor_chain(type, refs[:-1]) if len(refs) > 1 else type,
                "field_name": refs[-1]}


def build_tree(start, pairs, expression_type):
    ops = {"+": ("plus", "arith"), "-": ("minus", "arith"), "*": ("multiply", "arith"), "/": ("divide", "arith"),
           "%": ("modulo", "arith"),
           ">=": ("ge", "ord"), ">": ("gt", "ord"), "<": ("lt", "ord"), "<=": ("le", "ord"),
           "&&": ("and", "bool"), "||": ("or", "bool"), "!": ("not", "bool"),
           "==": ("eq", "equality"), "!=": ("ne", "equality")}
    for pair in pairs:
        if expression_type == "IfElse":
            start = {"expression": expression_type, "condition": start, "if_true": pair[1], "if_false": pair[2]}
        else:
            start = {"expression": "MethodInvocation", "method": ops[pair[0]][0], "self": pair[1],
                     "arguments": [{"name": "other", "value": start}]}
    return start


def filename_to_protocol_name(filename):
    split = re.split('[\./\\\]+', filename)
    return split[len(split)-2]
