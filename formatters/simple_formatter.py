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
from formatters.formatter import Formatter
from protocol import *

class SimpleFormatter(Formatter):
    output: List[str]
    parsers: Dict[str, str]

    def __init__(self):
        self.output = []
        self.parser = {}

    def generate_output(self):
        return "\n".join(self.output)

    def format_expression(self, expr:Expression):
        if type(expr) is ConstantExpression and type(expr.constant_type) is Number:
            return "%s" % (expr.constant_value)
        elif type(expr) is MethodInvocationExpression:
            operators = {"plus": "+",
                         "minus": "-",
                         "multiply": "*",
                         "divide": "/",
                         "modulo": "%",
                         "ge": ">=",
                         "gt": ">",
                         "lt": "<",
                         "le": "<=",
                         "and": "&&",
                         "or": "||",
                         "not": "!",
                         "eq": "==",
                         "ne": "!="}
            if expr.method_name in operators:
                return "(%s %s %s)" % (self.format_expression(expr.target), operators[expr.method_name], self.format_expression(expr.arg_exprs[0].arg_value))
            elif expr.method_name == "to_integer":
                return self.format_expression(expr.target)
        elif type(expr) is FieldAccessExpression:
            return expr.field_name

    def format_bitstring(self, bitstring:BitString):
        self.output.append("BitString ({}) [size: {} bits]".format(bitstring, self.format_expression(bitstring.size)))

    def format_struct(self, struct:Struct):
        self.output.append("Struct ({})".format(struct))

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
