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

from string import ascii_letters
import itertools

from protocol import *
from formatters.formatter import Formatter

class RustFormatter(Formatter):
    """
    Class to generate Rust code from parsed ASCII diagrams
    """

    output: List[str]

    #add necessary imports at the start of every generated rust file
    def __init__(self):
        self.output = []
        self.structs = {}
        #add crate/imports
        self.output.append("extern crate nom;\n\nuse nom::{bits::complete::take, combinator::map};\nuse nom::sequence::tuple;\nuse nom::error::ErrorKind;\nuse nom::Err::Error;\n\n")

    def generate_output(self):
        return "".join(self.output)

    #bitstrings are formatted as structs containing a single int to differentiate between bitstrings which serve different purposes (eg. Timestamp, SeqNum, PortNum)
    def format_bitstring(self, bitstring:BitString):
        if bitstring.name not in self.output:
            self.output.append("\n#[derive(Debug, PartialEq, Eq)]\n")
            self.output.extend(["struct ", bitstring.name, "(u%d);\n" % self.assign_int_size(bitstring)])

    #assign the smallest possible unsigned int which can accommodate the size given
    def assign_int_size(self, bitstring:BitString):
        #TODO: determine how to handle bitstrings which aren't given an explicit size
        if bitstring.size <= 8:
            return 8
        elif bitstring.size <= 16:
            return 16
        elif bitstring.size <= 32:
            return 32
        elif bitstring.size <= 64:
            return 64
        else:
            return 128

    def format_struct(self, struct:Struct):
        #traits need to be added up here when using !derive (eg. Eq, Ord)
        self.output.append("\n#[derive(Debug")
        for trait in struct.traits:
            if trait == "Equality":
                self.output.append(", PartialEq, Eq")
            elif trait == "Ordinal":
                self.output.append(", Ord")
        self.output.append(")]\n")
        self.output.extend(["struct ", struct.name.replace("-", "").replace(" ", ""), " {\n"])
        for field in struct.fields:
            self.output.append("    %s: %s,\n" % (field.field_name, field.field_type.name))
        self.output.append("}\n")

    def format_array(self, array:Array):
        if array.length is None:
            self.output.append("struct %s(Vec<%s" % (array.name, array.element_type.name))
            if array.element_type.kind == "BitString":
                self.output.append("(u%d)" % self.assign_int_size(array.element_type))
            self.output.append(">);")
        else:
            self.output.append("struct %s([%s" % (array.name, array.element_type.name))
            if array.element_type.kind == "BitString":
                self.output.append("(u%d)" % self.assign_int_size(array.element_type))
            self.output.append("; %d]);" % array.length)
        self.output.append("\n\n")

    def format_enum(self, enum:Enum):
        self.output.extend(["\nenum ", "%s {\n" % enum.name])
        for variant in enum.variants:
            self.output.append("    %s,\n" % variant.name)
        self.output.append("}\n\n")

    def format_function(self, function:Function):
        self.output.append("fn {function_name}(".format(function_name=function.name))
        for param in function.parameters:
            #TODO: handle parameters which aren't just structs
            self.output.append("{param_name}: {param_type}".format(param_name=param.param_name, param_type=param.param_type.name))
            if param not in function.parameters[-1:]:
                self.output.append(", ")
            else:
                self.output.append(") ")
        if function.return_type.kind != "Nothing":
            self.output.append("-> {return_type}".format(return_type=function.return_type.name))
        self.output.append(" {\n    //function body required\n    unimplemented!();\n}\n\n")

    def format_context(self, context:Context):
        for field in context.fields:
            #TODO: expand this to handle expressions when a numerical size is not present (ie. size was left undefined)
            if field.field_type.kind == "BitString":
                var_type = "u%d" % (self.assign_int_size(field.field_type))
            elif field.field_type.kind == "Option":
                var_type = "Option<{ref_type}>".format(ref_type=field.field_type.reference_type.name)
            #Nothing isn't included as a return type here - should be covered by Option
            elif field.field_type.kind == "Array":
                if field.field_type.length is None:
                    var_type = "Vec<{element_type}>".format(element_type=field.field_type.element_type.name)
                else:
                    if field.field_type.element_type.kind == "BitString":
                        var_type = "[%s(u%d); %d]" % (field.field_type.name, (self.assign_int_size(field.field_type.element_type)), field.field_type.length)
                    else:
                        var_type = "[%s; %d]" % (field.field_type.name, field.field_type.length)
            elif field.field_type.kind == "Struct":
                var_type = field.field_type.name
            elif field.field_type.kind == "Enum":
                var_type = field.field_type.name
            #FIXME: this will likely not work for all cases of derived types
            else:
                var_type = field.field_type.name

            #all variables are set to mutable for now
            self.output.append("let mut {var_name}: {var_type};\n".format(var_name=field.field_name, var_type=var_type))

    def closure_term_gen(self):
        for i in range(len(ascii_letters)):
            yield ascii_letters[i]

    def format_protocol(self, protocol:Protocol):
        defined_parsers = []
        for item in protocol.get_type_names():
            if protocol.get_type(item).kind == "Struct":
                parser_functions = []
                closure_terms = []
                generator = self.closure_term_gen()
                #write parsers for individual fields
                for field in protocol.get_type(item).fields:
                    if field.field_type.name.lower() not in defined_parsers:
                        if field.field_type.kind == "BitString":
                            self.output.append("\nfn parse_{fname}(input: (&[u8], usize)) -> nom::IResult<(&[u8], usize), {typename}>{{\n".format(fname=field.field_type.name.lower(), typename=field.field_type.name.replace("-", "").replace(" ", "")))
                            self.output.append("\n    map(take({size}_usize), |x| {name}(x))(input)\n}}\n".format(size=field.field_type.size, name=field.field_type.name))
                        defined_parsers.append(field.field_type.name.lower())
                    parser_functions.append("parse_{name}".format(name=field.field_type.name.lower()))
                    closure_terms.append("{term}".format(term=next(generator)))
                #write function to combine parsers to parse an entire PDU
                #TODO: make this use items in PDU field of protocol object, not just list of types (nothing currently in PDUs in test cases)
                self.output.append("\nfn parse_{fname}(input: (&[u8], usize)) -> nom::IResult<(&[u8], usize), {typename}>{{\n    ".format(fname=protocol.get_type(item).name.replace(" ", "_").replace("-", "_").lower(),typename=protocol.get_type(item).name.replace("-", "").replace(" ", "")))
                if protocol.get_type(item).constraints:
                    self.output.append("match ")
                self.output.append("map(tuple(({functions})), |({closure})| {name}{{".format(functions=", ".join(parser_functions), closure=", ".join(closure_terms), name=protocol.get_type(item).name.replace("-", "").replace(" ", "")))
                #check constraints
                #self.output.append("{struct}{{{values}}})(input)\n}}\n".format(struct=protocol.get_type(item).name, values=": ".join(map(str, list(itertools.chain(*(zip(iter(protocol.get_type_names()), iter(closure_terms)))))))))
                for i in range(len(protocol.get_type(item).fields)):
                    self.output.append("{f_name}: {closure_term}, ".format(f_name=protocol.get_type(item).fields[i].field_name, closure_term=closure_terms[i]))
                self.output.append("})(input)")

                for constraint in protocol.get_type(item).constraints:
                    #TODO: change from hardcoded '.0' to handle fields with more than one element (ie. arrays or tuples)
                    if protocol.get_type(item).constraints.index(constraint) == 0:
                        self.output.append(" {{\n        Ok((remain, parsed_value)) => \n        if parsed_value.{fieldname}.0 ".format(fieldname=constraint.target.field_name))
                    else:
                        self.output.append(" parsed_value.{fieldname}.0 ".format(fieldname=constraint.target.field_name))
                    #TODO: refactor this into something less bloated
                    if constraint.method_name == "eq":
                        self.output.append("== ")
                    elif constraint.method_name == "ne":
                        self.output.append("!= ")
                    elif constraint.method_name == "lt":
                        self.output.append("< ")
                    elif constraint.method_name == "le":
                        self.output.append("<= ")
                    elif constraint.method_name == "gt":
                        self.output.append("> ")
                    elif constraint.method_name == "ge":
                        self.output.append(">= ")
                    self.output.append("{term} ".format(term=constraint.arg_exprs[0].arg_value.constant_value))
                    if protocol.get_type(item).constraints.index(constraint)+1 == len(protocol.get_type(item).constraints):
                        self.output.append("{{\n            Ok((remain, parsed_value))\n        }} else {{\n            Err(Error((remain, ErrorKind::Verify)))\n        }}\n        Err(e) => {{\n            Err(e)\n        }}\n    }}".format())
                    else:
                        self.output.append("&&")
                self.output.append("\n}\n")
                defined_parsers.append(protocol.get_type(item).name.lower())
