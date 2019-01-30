# =================================================================================================
# Copyright (C) 2018-2019 University of Glasgow
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

from input_parsers.inputparser import InputParser
from protocol import Protocol 
from typing import Dict, List, Tuple, Optional, Any
import parsley
import string

from input_parsers.protocolbuilder import *
from protocoltypes import *

class PacketLangParser(InputParser):
    pb: ProtocolBuilder
    types: Dict[str,"Type"]

    def __init__(self):
        self.pb = ProtocolBuilder()

    def new_bitstring(self, name: str = None, size: int = None) -> BitStringConstructor:
        bitstring_constructor = BitStringConstructor(name=name, size=size)
        return bitstring_constructor

    def new_derivedtype(self, type_name: str, derived_from: str, implements: List[str]):
        return NewTypeConstructor(type_name, derived_from, implements)

    def new_array(self, element_type, name:str = None, length:int = None):
        if type(element_type) == BitStringConstructor:
            self.pb.add_definition(element_type, warn_if_defined=False)
            element_type = element_type.name

        array_constructor = ArrayConstructor(element_type, name=name, length=length)
        return array_constructor

    def new_typedef(self, name, type_constructor: TypeConstructor):
        type_constructor.name = name
        self.pb.add_definition(type_constructor)

    def new_struct(self, name, fields, constraints):
        constraints = [] if constraints == None else constraints
        struct_constructor = StructConstructor(name, fields, constraints, [])
        self.pb.add_definition(struct_constructor)
        
    def new_structfield(self, field_name: str, field_type, is_present: Expression = None, transform: Expression = None):
        if type(field_type) == BitStringConstructor:
            self.pb.add_definition(field_type, warn_if_defined=False)
            field_type = field_type.name

        field_type = self.pb.definitions[field_type].build_protocol_type()
        return StructField(field_name, field_type, ConstantExpression("Boolean", "True"), transform)

    def new_parameter(self, parameter_name: str, parameter_type: str):
        return Parameter(parameter_name, parameter_type)

    def new_argument(self, name: str, value: Any):
        return Argument(name, value)

    def new_func(self, func_name: str, parameters: List[Parameter], return_type: str):
        func_def = Function(func_name, parameters, return_type)
        self.pb.add_definition(func_def)

    def new_constant(self, type_name: str, value: Any):
        return ConstantExpression(type_name, value)

    def new_fieldaccess(self, target, field_name: str):
        return FieldAccessExpression(target, field_name)

    def new_this(self):
        return ThisExpression(Struct(None)) # FIXME

    def new_methodinvocation(self, target, method, arguments):
        arguments = [] if arguments == None else arguments
        return MethodInvocationExpression(target, method, arguments)

    def build_tree(self, start, pairs, expression_type):
        ops = {"+": ("plus", "arith"), "-": ("minus", "arith"), "*": ("multiply", "arith"), "/": ("divide", "arith"), "%": ("modulo", "arith"),
               ">=": ("ge", "ord"), ">": ("gt", "ord"), "<": ("lt", "ord"), "<=": ("le", "ord"),
               "&&": ("and", "bool"), "||": ("or", "bool"), "!": ("not", "bool"),
               "==": ("eq", "equality"), "!=": ("ne", "equality")}
        for pair in pairs:
            if expression_type == "IfElse":
                start = {"expression": expression_type, "condition": start, "if_true": pair[1], "if_false": pair[2]}
            else:
                start = MethodInvocationExpression(pair[1], ops[pair[0]][0], [Argument("other", start)])
        return start

    def set_pdus(self, pdu_names):
        for pdu_name in pdu_names:
            self.pb.add_pdu(pdu_name)

    def build_protocol(self, input_str: str, name: str = None) -> Protocol:
        self.pb.set_protocol_name(name)
             
        # load grammar
        with open("input_parsers/packetlang/packetlang_grammar.txt", "r+") as grammarFile:
            grammar = grammarFile.read()
        
        # create parser
        parser = parsley.makeGrammar(grammar, {"ascii_letters"        : string.ascii_letters,
                                               "ascii_uppercase"      : string.ascii_uppercase,
                                               "ascii_lowercase"      : string.ascii_lowercase,
                                               "new_bitstring"        : self.new_bitstring,
                                               "new_typedef"          : self.new_typedef,
                                               "new_array"            : self.new_array,
                                               "new_structfield"      : self.new_structfield,
                                               "new_struct"           : self.new_struct,
                                               "new_parameter"        : self.new_parameter,
                                               "new_func"             : self.new_func,
                                               "new_constant"         : self.new_constant,
                                               "new_fieldaccess"      : self.new_fieldaccess,
                                               "new_this"             : self.new_this,
                                               "new_methodinvocation" : self.new_methodinvocation,
                                               "build_tree"           : self.build_tree,
                                               "set_pdus"             : self.set_pdus})
        
        # parse input
        parser(input_str.replace(" ", "").replace("\n", "").replace("\t", "")).protocol()

        return self.pb.build_protocol()
 
    def get_json_constructors(self) -> str:
        return self.pb.get_json_constructor()
        
def get_parser() -> PacketLangParser:
    return PacketLangParser()