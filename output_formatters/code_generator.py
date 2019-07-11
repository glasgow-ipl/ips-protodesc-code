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
    structs : Dict[Struct, list[StructField]]

    def __init__(self):
        self.output = []
        self.structs = {}

    def generate_output(self):
        pass


    def format_bitstring(self, bitstring:BitString):
        pass


    def format_struct(self, struct:Struct):
        #traits need to be added up here if we're using !derive (eg. Sized, Eq)
        self.output.append("struct %s\n {" % (struct.name))
        for field in struct.fields:
            #need to add type annotations for each field
            self.output.append("\t%s\n" % (field.name))
        self.output.append("}\n")

    def format_array(self, array:Array):
        pass


    def format_enum(self, enum:Enum):
        pass


    def format_function(self, function:Function):
        pass


    def format_context(self, context:Context):
        pass


    def format_protocol(self, protocol:Protocol):
        pass
        #loop format_struct
        for item in protocol.get_type_names():
            if type(item) is Struct:
                self.format_struct(protocol.get_type(item))