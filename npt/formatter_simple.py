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

import abc
from typing        import Optional, List, Any
from npt.protocol  import *
from npt.formatter import Formatter

class SimpleFormatter(Formatter):
    output: List[str]
    parsers: Dict[str, str]

    def __init__(self):
        self.output = []
        self.parser = {}

    def generate_output(self):
        return "\n".join(self.output)

    def format_argumentexpression(self, arg_name: str, arg_value: Any) -> Any:
        return "{}={}".format(arg_name, arg_value)

    def format_methodinvocationexpr(self, target: Any, method_name: str, arg_exprs: List[Any]) -> Any:
        if len(arg_exprs) == 0:
            arg_exprs_str = ""
        else:
            arg_exprs_str = ",".join(arg_exprs)
        return "{}.{}({})".format(target, method_name, arg_exprs_str)

    def format_functioninvocationexpr(self, func_name: str, args_exprs: List[Any]) -> Any:
        return "{}({})".format(func_name, args_exprs)

    def format_fieldaccessexpr(self, target: Any, field_name: str) -> Any:
        return "{}.{}".format(target, field_name)

    def format_contextaccessexpr(self, field_name: str) -> Any:
        return "Context.{}".format(field_name)

    def format_ifelseexpr(self, condition: Any, if_true: Any, if_false: Any) -> Any:
        return "({}) ? {} : {}".format(condition, if_true, if_false)

    def format_selfexpr(self) -> Any:
        return "Self"

    def format_constantexpr(self, constant_type: ProtocolType, constant_value: Any) -> Any:
        return str(constant_value)

    def format_expression(self, expr:Any):
        return str(expr)

    def format_bitstring(self, bitstring:BitString, size: str):
        self.output.append("BitString ({}) [size: {} bits]".format(bitstring, size))

    def format_struct(self, struct:Struct, constraints: List[str]):
        self.output.append("Struct ({})".format(struct))
        for field in struct.fields:
            self.output.append("\tField ({})".format(field))
        for constraint in constraints:
            self.output.append("\tConstraint ({})".format(constraint))
        for action in struct.actions:
            self.output.append("\tAction ({})".format(action))

    def format_array(self, array:Array):
        self.output.append("Array ({})".format(array))

    def format_enum(self, enum:Enum):
        self.output.append("Enum ({})".format(enum))

    def format_function(self, function:Function):
        self.output.append("Function ({})".format(function))

    def format_context(self, context:Context):
        self.output.append("Context ({})".format(context))
        for field in context.fields:
            self.output.append("\tField ({})".format(field))

    def format_protocol(self, protocol:Protocol):
        self.format_context(protocol.get_context())
        self.output.append("Protocol ({})\n".format(protocol.get_protocol_name()))
