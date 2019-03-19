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

import abc
from output_formatters.outputformatter import OutputFormatter
from protocol import * 

class CParserGenerator(OutputFormatter):
    output: List[str]
    parsers: Dict[str, str]
    
    def __init__(self):
        self.typedefs = []
        self.output = []
        self.parser = {}

    def generate_output(self):
        with open("output_formatters/cparsergenerator/bitreader.c", "r") as bitReaderSrcFile:
            bitReaderSrc = bitReaderSrcFile.read()
        libs = "#include <stdint.h>\n#include <stdio.h>\n#include <string.h>\n#include <stdlib.h>\n"
        self.output = [libs] + ["\n\n".join(self.typedefs)] + [bitReaderSrc] + self.output
        return "\n".join(self.output)

    def format_bitstring(self, bitstring:BitString):
        bitstring_typedef = "typedef struct %s {\n    uint8_t *value;\n    int width;\n} %s;" % (bitstring.name, bitstring.name)
        self.typedefs.append(bitstring_typedef)

    def format_struct(self, struct:Struct):
        self.output.append("Struct ({})".format(struct))
        # construct fields
        field_defs = []
        for field in struct.fields:
            if field.field_type.name == "BitString$None":
                field_def = "Bits %s[];" % (field.field_name)
            else:
                field_def = "%s %s;" % (field.field_type.name, field.field_name)
            field_defs.append("    " + field_def);
            
        # construct struct definition
        struct_def = "typedef struct %s {\n%s\n} %s;" % (struct.name, "\n".join(field_defs), struct.name)
        self.typedefs.append(struct_def)

    def format_array(self, array:Array):
        self.output.append("Array ({})".format(array))
        
    def format_enum(self, enum:Enum):
        self.output.append("Enum ({})".format(enum))

    def format_function(self, function:Function):
        self.output.append("Function ({})".format(function))

    def format_context(self, context:Context):
        self.output.append("Context ({})".format(context))

    def format_protocol(self, protocol:Protocol):
        self.output.append("Protocol ({})\n".format(protocol.get_protocol_name()))
