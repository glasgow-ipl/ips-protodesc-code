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

from typing       import Optional, List, Any
from npt.protocol import *

class Formatter(abc.ABC):
    """
    Abstract class for output formatters.
    """

    @abc.abstractmethod
    def generate_output(self):
        pass

    @abc.abstractmethod
    def format_expression(self, carry: Any) -> str:
        pass

    @abc.abstractmethod
    def format_argumentexpression(self, arg_name: str, arg_value: Any) -> Any:
        pass

    @abc.abstractmethod
    def format_methodinvocationexpr(self, target: Any, method_name: str, arg_exprs: List[Any]) -> Any:
        pass

    @abc.abstractmethod
    def format_functioninvocationexpr(self, func_name: str, args_exprs: List[Any]) -> Any:
        pass

    @abc.abstractmethod
    def format_fieldaccessexpr(self, target: Any, field_name: str) -> Any:
        pass

    @abc.abstractmethod
    def format_contextaccessexpr(self, field_name: str) -> Any:
        pass

    @abc.abstractmethod
    def format_ifelseexpr(self, condition: Any, if_true: Any, if_false: Any) -> Any:
        pass

    @abc.abstractmethod
    def format_selfexpr(self) -> Any:
        pass

    @abc.abstractmethod
    def format_constantexpr(self, constant_type: str, constant_value: Any) -> Any:
        pass

    @abc.abstractmethod
    def format_bitstring(self, bitstring: BitString, size: str):
        pass

    @abc.abstractmethod
    def format_struct(self, struct:Struct, constraints: List[str]):
        pass

    @abc.abstractmethod
    def format_array(self, array:Array):
        pass

    @abc.abstractmethod
    def format_enum(self, enum:Enum):
        pass

    @abc.abstractmethod
    def format_function(self, function:Function):
        pass

    @abc.abstractmethod
    def format_context(self, context:Context):
        pass

    @abc.abstractmethod
    def format_protocol(self, protocol:Protocol):
        pass

