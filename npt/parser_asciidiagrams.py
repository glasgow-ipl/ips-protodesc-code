# =================================================================================================
# Copyright (C) 2018-2020 University of Glasgow
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

from parser import Parser

import rfc
import protocol
import parsley
import string

def stem(phrase):
    if phrase[-1] == 's':
        return phrase[:-1]
    else:
        return phrase

def valid_field_name_convertor(name):
    if name is not None:
        return name.lower().replace(" ", "_")
    else:
        return None

def valid_type_name_convertor(name):
    if name[0].isdigit():
        name = "T" + name
    return name.capitalize().replace(" ", "_")

class AsciiDiagramsParser(Parser):
    def __init__(self) -> None:
        super().__init__()

    def new_field(self, full_label, short_label, size, units, value_constraint, is_present, is_array):
        return {"full_label": valid_field_name_convertor(full_label), "short_label": valid_field_name_convertor(short_label), "size": size, "units": units, "value_constraint": value_constraint, "is_present": is_present, "is_array": is_array}

    def new_this(self):
        return ("this")

    def new_methodinvocation(self, target, method, arguments):
        return("methodinvocation", target, method, arguments)

    def new_fieldaccess(self, target, field_name):
        return ("fieldaccess", target, field_name)

    def new_constant(self, type_name, value):
        return ("const", type_name, value)

    def build_tree(self, start, pairs, expression_type):
        ops = {"^" : ("pow", "arith"), "+": ("plus", "arith"), "-": ("minus", "arith"), "*": ("multiply", "arith"), "/": ("divide", "arith"), "%": ("modulo", "arith"),
               ">=": ("ge", "ord"), ">": ("gt", "ord"), "<": ("lt", "ord"), "<=": ("le", "ord"),
               "&&": ("and", "bool"), "||": ("or", "bool"), "!": ("not", "bool"), "and": ("and", "bool"), "or": ("or", "bool"), "not": ("not", "bool"),
               "==": ("eq", "equality"), "!=": ("ne", "equality")}
        for pair in pairs:
            if expression_type == "IfElse":
                start = ("ifelse", start, pair[1], pair[2])
            else:
                start = ("method", start, ops[pair[0]][0], pair[1])
        return start

    def proc_diagram_fields(self, diagram_fields):
        clean_diagram_fields = []
        bits = 0
        label = None
        for field in diagram_fields:
            if field == None:
                if bits != 0 and label is not None:
                    clean_diagram_fields.append((bits, label))
                continue
            if ':' in field[1]:
                field = ("var", field[1].replace(':', '').strip())
            if field[1] == '' and type(field[0]) is int:
                bits = bits + field[0]
                continue
            if field[1] == '+                                                               +':
                continue
            if len(field[1]) > 0 and field[1][0] == '+' and field[1][-1] == '+':
                label = field[1][1:-1].strip()
                continue
            clean_diagram_fields.append(field)
        return clean_diagram_fields

    def build_parser(self):
        self.structs = {}
        self.enums = {}
        self.functions = {}
        self.serialise_to = {}
        self.parse_from = {}
        with open("parsers/asciidiagrams/asciidiagrams-grammar.txt") as grammarFile:
            return parsley.makeGrammar(grammarFile.read(),
                                   {
                                     "ascii_uppercase"         : string.ascii_uppercase,
                                     "ascii_lowercase"         : string.ascii_lowercase,
                                     "ascii_letters"           : string.ascii_letters,
                                     "punctuation"             : string.punctuation,
                                     "new_constant"            : self.new_constant,
                                     "build_tree"              : self.build_tree,
                                     "new_fieldaccess"         : self.new_fieldaccess,
                                     "new_methodinvocation"    : self.new_methodinvocation,
                                     "new_this"                : self.new_this,
                                     "new_field"               : self.new_field,
                                     "proc_diagram_fields"     : self.proc_diagram_fields,
                                     "stem"                    : stem,
                                     "protocol"                : self.proto
                                   })

    def process_section(self, section : rfc.Section, parser, structs):
        for i in range(len(section.content)):
            if type(section.content[i]) is rfc.T:
                try:
                    pdu_name = parser(section.content[i].content[-1]).preamble()
                    artwork = section.content[i+1]
                    artwork_fields = parser(artwork.content.strip()).diagram()
                    where = section.content[i+2]
                    desc_list = section.content[i+3]
                    fields = {}
                    name_map = {}
                    for i in range(len(desc_list.content)):
                        title, desc = desc_list.content[i]
                        field = parser(title.content[-1]).field_title()
                        context_field = parser(desc.content[-1]).context_use()
                        field["context_field"] = context_field
                        if field["short_label"] is not None:
                            name_map[field["short_label"]] = field["full_label"]
                        fields[field["full_label"]] = field

                    self.structs[valid_type_name_convertor(pdu_name)] = {}
                    self.structs[valid_type_name_convertor(pdu_name)]["name_map"] = name_map
                    self.structs[valid_type_name_convertor(pdu_name)]["fields"] = fields
                except Exception as e:
                    pass

                try:
                    function_name = parser(section.content[i].content[-1]).function()
                    function_def = parser(section.content[i+1].content.strip()).function_signature()
                    self.functions[valid_field_name_convertor(function_name)] = function_def
                except Exception as e:
                    pass

                try:
                    enum_name, variants = parser(section.content[i].content[-1]).enum()
                    self.enums[valid_type_name_convertor(enum_name)] = [valid_type_name_convertor(variant) for variant in variants]
                except Exception as e:
                    pass

                try:
                    from_type, to_type, func_name = parser(section.content[i].content[-1]).serialised_to_func()
                    self.serialise_to[valid_type_name_convertor(from_type)] = (valid_type_name_convertor(to_type), valid_field_name_convertor(func_name))
                except Exception as e:
                    pass

                try:
                    from_type, to_type, func_name = parser(section.content[i].content[-1]).parsed_from_func()
                    self.parse_from[valid_type_name_convertor(from_type)] = (valid_type_name_convertor(to_type), valid_field_name_convertor(func_name))
                except Exception as e:
                    pass

                try:
                    protocol_name, pdus = parser(section.content[i].content[-1]).protocol_definition()
                    self.protocol_name = protocol_name
                    self.pdus = [valid_type_name_convertor(pdu) for pdu in pdus]
                except Exception as e:
                    continue
        for subsection in section.sections:
            self.process_section(subsection, parser, structs)

    def build_expr(self, expr, pdu_name):
        if type(expr) != tuple:
            if expr == "this":
                return protocol.SelfExpression()
            if type(expr) is not str:
                return expr
            return self.structs[pdu_name]["name_map"].get(valid_field_name_convertor(expr), valid_field_name_convertor(expr))
        elif expr[0] == "contextaccess":
            return protocol.ContextAccessExpression(self.proto.get_context(), valid_field_name_convertor(expr[1]))
        elif expr[0] == "setvalue":
            return protocol.MethodInvocationExpression(self.build_expr(expr[1], pdu_name), "set", [protocol.ArgumentExpression("value", self.build_expr(expr[2], pdu_name))])
        elif expr[0] == "const":
            return protocol.ConstantExpression(self.build_type(expr[1]), self.build_expr(expr[2], pdu_name))
        elif expr[0] == "method":
            return protocol.MethodInvocationExpression(self.build_expr(expr[1], pdu_name), expr[2], [protocol.ArgumentExpression("other", self.build_expr(expr[3], pdu_name))])
        elif expr[0] == "methodinvocation":
            return protocol.MethodInvocationExpression(self.build_expr(expr[1], pdu_name), expr[2], expr[3])
        elif expr[0] == "fieldaccess":
            target = self.build_expr(expr[1], pdu_name)
            if type(target) == protocol.FieldAccessExpression:
                pdu_name = valid_type_name_convertor(self.structs[pdu_name]["fields"][valid_field_name_convertor(target.field_name)]["units"])
            return protocol.FieldAccessExpression(target, self.build_expr(expr[2], pdu_name))

    def build_struct(self, struct_name):
        fields = []
        constraints = []
        actions = []
        for field in self.structs[struct_name]["fields"]:
            field = self.structs[struct_name]["fields"][field]
            size_expr = None
            ispresent_expr = None
            if field["units"] not in ["bits", "bit", "bytes", "byte", None]:
                if field["is_array"]:
                    name = struct_name + "_" + field["full_label"]
                    field_type = self.proto.define_array(name, self.build_type(valid_type_name_convertor(field["units"])), None)
                else:
                    field_type = self.build_type(valid_type_name_convertor(field["units"]))
            if field["size"] is not None:
                if field["size"][0] == "methodinvocation" or field["size"][0] == "method":
                    size_expr = self.build_expr(("method", field["size"], "eq", ("methodinvocation", ("fieldaccess", "this", field["full_label"]), "size", [])), struct_name)
                else:
                    size_expr = self.build_expr(field["size"], struct_name)
            if field["value_constraint"] is not None:
                value_expr = self.build_expr(field["value_constraint"], struct_name)
                constraints.append(value_expr)
            if field["units"] in ["bits", "bit", "bytes", "byte", None]:
                name = struct_name + "_" + field["full_label"]
                if type(size_expr) is protocol.ConstantExpression and field["units"] in ["byte", "bytes"]:
                    size_expr = self.build_expr(("const", "Number", size_expr.constant_value*8), struct_name)
                if type(size_expr) is protocol.ConstantExpression:
                    field_type = self.proto.define_bitstring(name, size_expr)
                else:
                    field_type = self.proto.define_bitstring(name, None)
                    if size_expr is not None:
                        constraints.append(size_expr)
            if field["is_present"] is not None:
                ispresent_expr = self.build_expr(field["is_present"], struct_name)
            else:
                ispresent_expr = self.build_expr(("const", "Boolean", True), struct_name)
            if field["context_field"] is not None:
                self.proto.define_context_field(valid_field_name_convertor(field["context_field"][1]), self.build_type("Number"))
                action = self.build_expr(("setvalue", ("contextaccess", field["context_field"][1]), field["context_field"][0]), struct_name)
                actions.append(action)
            struct_field = protocol.StructField(field["full_label"],
                                                field_type,
                                                ispresent_expr)
            fields.append(struct_field)
        struct = self.proto.define_struct(struct_name, fields, constraints, actions)
        return struct

    def build_enum(self, type_name):
        variants = []
        for variant in self.enums[type_name]:
            variants.append(self.build_type(variant))
        enum = self.proto.define_enum(type_name, variants)
        if type_name in self.serialise_to:
            func_type = self.build_type(self.serialise_to[type_name][1])
            enum.set_serialise_to_func(func_type)
        if type_name in self.parse_from:
            func_type = self.build_type(self.parse_from[type_name][1])
            enum.set_parse_from_func(func_type)
        return enum

    def build_function(self, type_name):
        name = type_name
        parameters = []
        for param_name, param_type_name in self.functions[type_name][1]:
            param_type = self.build_type(valid_type_name_convertor(param_type_name))
            parameters.append(protocol.Parameter(param_name, param_type))
        function = self.proto.define_function(name, parameters, self.build_type(valid_type_name_convertor(self.functions[type_name][2])))
        return function

    def build_type(self, type_name):
        if self.proto.has_type(type_name):
            return self.proto.get_type(type_name)
        elif type_name in self.structs:
            return self.build_struct(type_name)
        elif type_name in self.enums:
            return self.build_enum(type_name)
        elif type_name in self.functions:
            return self.build_function(type_name)
        else:
            raise Exception("Unknown type: %s" % (type_name))

    def build_protocol(self, proto: protocol.Protocol, input: rfc.RFC, name: str=None) -> protocol.Protocol:
        # if a Protocol hasn't been passed in, then instantiate one
        if proto is None:
            self.proto = protocol.Protocol()
        else:
            self.proto = proto

        # make parser
        parser = self.build_parser()

        # find matching preambles
        structs = []

        for section in input.middle.content:
            self.process_section(section, parser, structs)

        for pdu_name in self.pdus:
            self.build_type(pdu_name)
            self.proto.define_pdu(pdu_name)

        self.proto.set_protocol_name(self.protocol_name)

        return self.proto
