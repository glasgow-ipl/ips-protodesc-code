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

from protocol import *
from output_formatters.outputformatter import OutputFormatter

class CodeGenerator(OutputFormatter):
    """
    Class to generate code from parsed ASCII diagrams - currently only produces Rust
    """

    output: List[str]

    def __init__(self):
        self.output = []
        self.structs = {}

    def generate_output(self):
        pass


    def format_bitstring(self, bitstring:BitString):
        self.output.append("    %s: " % bitstring.name)
        #assign the smallest possible unsigned int which can accommodate the field
        if bitstring.size <= 8:
            self.output.append(" u%d" % 8)
        elif bitstring.size <= 16:
            self.output.append(" u%d" % 16)
        elif bitstring.size <= 32:
            self.output.append(" u%d" % 32)
        elif bitstring.size <= 64:
            self.output.append(" u%d" % 64)
        else:
            self.output.append(" u%d" % 128)


    def format_struct(self, struct:Struct):
        #traits need to be added up here if we're using !derive (eg. Eq, Ord)
        #including Debug trait by default - this may be changed later
        self.output.append("#[derive(Debug")
        for trait in struct.traits:
            if trait == "Equality":
                self.output.append(", Eq")
            elif trait == "Ordinal":
                self.output.append(", Ord")
        self.output.append(")]\n")
        self.output.append("struct %s {\n" % struct.name)
        print(struct.fields)
        for field in struct.fields:
            if field.field_type.kind == "BitString":
                self.format_bitstring(field.field_type)
            if struct.fields.index(field) != len(struct.fields) - 1:
                self.output.append(",\n")
            else:
                self.output.append("\n")
        self.output.append("}\n\n")

    def format_array(self, array:Array):
        pass


    def format_enum(self, enum:Enum):
        pass


    def format_function(self, function:Function):
        pass


    def format_context(self, context:Context):
        pass


    def format_protocol(self, protocol:Protocol):
        #print(protocol.get_type_names())
        for item in protocol.get_type_names():
            #print(protocol.get_type(item).kind)
            if protocol.get_type(item).kind == "Struct":
                self.format_struct(protocol.get_type(item))
        print("\n\n")
        print("".join(self.output))
