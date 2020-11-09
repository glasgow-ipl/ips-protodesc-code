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

import string
import parsley

import npt.rfc as rfc
import npt.protocol

from npt.parser import Parser
from typing     import cast, Optional, Union, List, Tuple

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
    name = ' '.join(name.replace('\n',' ').split())
    return name.capitalize().replace(" ", "_")

def resolve_multiline_length(tokens):
    # scan for variable length
    length = "var"  if len([ delim for desc, delim, length in tokens if delim in [ ':', '...' ]]) > 0 \
                    else max([ length for desc, delim, length in tokens])

    return ( length , " ".join([ desc for desc, delim, length in tokens if len(desc) > 0 ]))

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
        with open("npt/grammar_asciidiagrams.txt") as grammarFile:
            return parsley.makeGrammar(grammarFile.read(),
                                   {
                                     "ascii_uppercase"          : string.ascii_uppercase,
                                     "ascii_lowercase"          : string.ascii_lowercase,
                                     "ascii_letters"            : string.ascii_letters,
                                     "punctuation"              : string.punctuation,
                                     "new_constant"             : self.new_constant,
                                     "build_tree"               : self.build_tree,
                                     "new_fieldaccess"          : self.new_fieldaccess,
                                     "new_methodinvocation"     : self.new_methodinvocation,
                                     "new_this"                 : self.new_this,
                                     "new_field"                : self.new_field,
                                     "proc_diagram_fields"      : self.proc_diagram_fields,
                                     "stem"                     : stem,
                                     "resolve_multiline_length" : resolve_multiline_length,
                                     "protocol"                 : self.proto
                                   })

    def process_diagram(self, artwork: str, parser) -> List[Tuple[Union[int, str], str]]:
        delim_units = parser(artwork.strip()).diagram()
        fields : List[Tuple[Union[int, str], str]] = []

        for d_unit in delim_units:
            hlines =  d_unit.split(sep="\n")
            begin, end = hlines[0][0], hlines[0][-1] if hlines[0][-1] in ['|', ':'] else '...'
            min_sep = 2 if end == '|' else 1
            if len(hlines) == 1:
                fl = parser(d_unit).one_line()
            elif hlines[0].count('|') == min_sep:
                fl = parser(d_unit).multi_line()
            else:
                split_fields = []
                for line in hlines:
                    vertical_fragments = parser(line).one_line()
                    split_fields.append(vertical_fragments)

                num_lines = len(split_fields)
                num_fields = len(split_fields[0]) if num_lines > 0 else 0
                fl = [( split_fields[0][j][0],
                        "".join([split_fields[i][j][1] for i in range(num_lines)]))
                        for j in range(num_fields)]
            fields += fl
        return fields


    def process_section(self, section : rfc.Section, parser, structs):
        for i in range(len(section.content)):
            t = section.content[i]
            if isinstance(t, rfc.T):
                for j in range(len(t.content)):
                    inner_t = cast(rfc.Text, t.content[j])
                    try:
                        pdu_name = parser(inner_t.content.strip()).preamble()
                        artwork = cast(rfc.Artwork, section.content[i+1]).content
                        artwork_fields = self.process_diagram( cast(rfc.Text, artwork).content, parser)
                        where = section.content[i+2]
                        desc_list = cast(rfc.DL, section.content[i+3])
                        fields = {}
                        name_map = {}
                        for k in range(len(desc_list.content)):
                            title, desc = desc_list.content[k]
                            field = parser(cast(rfc.Text, title.content[0]).content.strip()).field_title()
                            try:
                                context_field = parser(cast(rfc.Text, desc.content[-1]).content.strip()).context_use()
                            except:
                                context_field = None
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
                        function_name = parser(inner_t.content.strip()).function()
                        function_artwork = cast(rfc.Artwork, section.content[i+1])
                        function_text = cast(rfc.Text, function_artwork.content)
                        function_def = parser(function_text.content.strip()).function_signature()
                        self.functions[valid_field_name_convertor(function_name)] = function_def
                    except Exception as e:
                        pass

                    try:
                        enum_name, variants = parser(inner_t.content.strip()).enum()
                        self.enums[valid_type_name_convertor(enum_name)] = [valid_type_name_convertor(variant) for variant in variants]
                    except Exception as e:
                        pass

                    try:
                        from_type, to_type, func_name = parser(inner_t.content.strip()).serialised_to_func()
                        self.serialise_to[valid_type_name_convertor(from_type)] = (valid_type_name_convertor(to_type), valid_field_name_convertor(func_name))
                    except Exception as e:
                        pass

                    try:
                        from_type, to_type, func_name = parser(inner_t.content.strip()).parsed_from_func()
                        self.parse_from[valid_type_name_convertor(from_type)] = (valid_type_name_convertor(to_type), valid_field_name_convertor(func_name))
                    except Exception as e:
                        pass

                    try: 
                        protocol_name, pdus = parser(inner_t.content.strip()).protocol_definition()
                        self.protocol_name = protocol_name
                        self.pdus = [valid_type_name_convertor(pdu) for pdu in pdus]
                    except Exception as e:
                        continue
        if section.sections is not None:
            for subsection in section.sections:
                self.process_section(subsection, parser, structs)

    def build_expr(self, expr, pdu_name):
        if type(expr) != tuple:
            if expr == "this":
                return npt.protocol.SelfExpression()
            if type(expr) is not str:
                return expr
            return self.structs[pdu_name]["name_map"].get(valid_field_name_convertor(expr), valid_field_name_convertor(expr))
        elif expr[0] == "contextaccess":
            return npt.protocol.ContextAccessExpression(self.proto.get_context(), valid_field_name_convertor(expr[1]))
        elif expr[0] == "setvalue":
            return npt.protocol.MethodInvocationExpression(self.build_expr(expr[1], pdu_name), "set", [npt.protocol.ArgumentExpression("value", self.build_expr(expr[2], pdu_name))])
        elif expr[0] == "const":
            return npt.protocol.ConstantExpression(self.build_type(expr[1]), self.build_expr(expr[2], pdu_name))
        elif expr[0] == "method":
            return npt.protocol.MethodInvocationExpression(self.build_expr(expr[1], pdu_name), expr[2], [npt.protocol.ArgumentExpression("other", self.build_expr(expr[3], pdu_name))])
        elif expr[0] == "methodinvocation":
            return npt.protocol.MethodInvocationExpression(self.build_expr(expr[1], pdu_name), expr[2], expr[3])
        elif expr[0] == "fieldaccess":
            target = self.build_expr(expr[1], pdu_name)
            if type(target) == npt.protocol.FieldAccessExpression:
                pdu_name = valid_type_name_convertor(self.structs[pdu_name]["fields"][valid_field_name_convertor(target.field_name)]["units"])
            return npt.protocol.FieldAccessExpression(target, self.build_expr(expr[2], pdu_name))

    def build_struct(self, struct_name):
        fields = []
        constraints = []
        actions = []
        for field in self.structs[struct_name]["fields"]:
            field = self.structs[struct_name]["fields"][field]
            size_expr = None
            ispresent_expr = None
            field_type : Optional[npt.protocol.RepresentableType] = None
            if field["units"] not in ["bits", "bit", "bytes", "byte", None]:
                if field["is_array"]:
                    name = struct_name + "_" + field["full_label"]
                    bitsize_expr = self.build_expr(field["value_constraint"], struct_name)
                    array_size = None
                    if isinstance(bitsize_expr, npt.protocol.MethodInvocationExpression) and \
                       isinstance(bitsize_expr.target, npt.protocol.MethodInvocationExpression) and \
                       isinstance(bitsize_expr.target.target, npt.protocol.FieldAccessExpression) and \
                       isinstance(bitsize_expr.target.target.target, npt.protocol.SelfExpression) and \
                       bitsize_expr.target.target.field_name == field["full_label"] and \
                       bitsize_expr.target.method_name == "size" and \
                       bitsize_expr.method_name == "eq":
                        array_size = bitsize_expr.arg_exprs[0].arg_value
                        field["value_constraint"] = None
                    field_type = npt.protocol.Array(name, self.build_type(valid_type_name_convertor(field["units"])), None, size=array_size)
                    self.proto.add_type(field_type)
                else:
                    field_type = self.build_type(valid_type_name_convertor(field["units"]))
            if field["size"] is not None:
                #if field["size"][0] == "methodinvocation" or field["size"][0] == "method":
                #    size_expr = self.build_expr(("method", field["size"], "eq", ("methodinvocation", ("fieldaccess", "this", field["full_label"]), "size", [])), struct_name)
                #else:
                size_expr = self.build_expr(field["size"], struct_name)
            if field["value_constraint"] is not None:
                value_expr = self.build_expr(field["value_constraint"], struct_name)
                constraints.append(value_expr)
            if field["units"] in ["bits", "bit", "bytes", "byte", None]:
                name = struct_name + "_" + field["full_label"]
                if size_expr is not None and type(size_expr) is npt.protocol.ConstantExpression and field["units"] in ["byte", "bytes"]:
                    size_expr = self.build_expr(("const", "Number", size_expr.constant_value*8), struct_name)
                elif size_expr is not None and field["units"] in ["byte", "bytes"]:
                    size_expr = self.build_expr(("method", size_expr, "multiply", ("const", "Number", 8)), struct_name)
                if type(size_expr) is npt.protocol.ConstantExpression:
                    field_type = npt.protocol.BitString(name, size_expr)
                    self.proto.add_type(field_type)
                else:
                    field_type = npt.protocol.BitString(name, size_expr)
                    self.proto.add_type(field_type)
                    #if size_expr is not None:
                    #    constraints.append(size_expr)
            else:
                if size_expr is not None and not(type(size_expr) is npt.protocol.ConstantExpression and size_expr.constant_value == 1) and isinstance(field_type, npt.protocol.RepresentableType):
                    field_type = npt.protocol.Array(struct_name + "_" + field["full_label"], field_type, size_expr)
                    self.proto.add_type(field_type)
            if field["is_present"] is not None:
                ispresent_expr = self.build_expr(field["is_present"], struct_name)
            else:
                ispresent_expr = self.build_expr(("const", "Boolean", True), struct_name)
            if field["context_field"] is not None:
                self.proto.get_context().add_field(npt.protocol.ContextField(valid_field_name_convertor(field["context_field"][1]), self.build_type("Number")))
                action = self.build_expr(("setvalue", ("contextaccess", field["context_field"][1]), field["context_field"][0]), struct_name)
                actions.append(action)
            if field_type is not None:
                struct_field = npt.protocol.StructField(field["full_label"],
                                                field_type,
                                                ispresent_expr)
            fields.append(struct_field)
        struct = self.proto.add_type(npt.protocol.Struct(struct_name, fields, constraints, actions))
        return struct

    def build_enum(self, type_name):
        variants = []
        for variant in self.enums[type_name]:
            variants.append(self.build_type(variant))
        enum = self.proto.add_type(npt.protocol.Enum(type_name, variants))
        if type_name in self.serialise_to:
            func_type = self.build_type(self.serialise_to[type_name][1])
            #enum.set_serialise_to_func(func_type)
        if type_name in self.parse_from:
            func_type = self.build_type(self.parse_from[type_name][1])
            #enum.set_parse_from_func(func_type)
        return enum

    def build_function(self, type_name):
        name = type_name
        parameters = []
        for param_name, param_type_name in self.functions[type_name][1]:
            param_type = self.build_type(valid_type_name_convertor(param_type_name))
            parameters.append(npt.protocol.Parameter(param_name, param_type))
        function = self.proto.add_type(npt.protocol.Function(name, parameters, self.build_type(valid_type_name_convertor(self.functions[type_name][2]))))
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
        elif type_name == "Number":
            return npt.protocol.Number()
        elif type_name == "Boolean":
            return npt.protocol.Boolean()
        elif type_name == "Nothing":
            return npt.protocol.Nothing()
        else:
            raise Exception("Unknown type: %s" % (type_name))

    def build_protocol(self, proto: Optional[npt.protocol.Protocol], input: Union[str, rfc.RFC], name: str=None) -> npt.protocol.Protocol:
        # if a Protocol hasn't been passed in, then instantiate one
        if proto is None:
            self.proto = npt.protocol.Protocol()
        else:
            self.proto = proto

        # make parser
        parser = self.build_parser()

        # find matching preambles
        structs : List[npt.protocol.Struct]= []

        if isinstance(input, rfc.RFC):
            for section in input.middle.content:
                self.process_section(section, parser, structs)

        for pdu_name in self.pdus:
            self.build_type(pdu_name)
            self.proto.define_pdu(pdu_name)

        self.proto.set_protocol_name(self.protocol_name)

        return self.proto
