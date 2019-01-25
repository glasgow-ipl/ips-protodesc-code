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

from typing import Dict, List, Tuple, Optional, Any
from protocoltypes import *
from protocoltypeelements import JSONRepresentable

# =================================================================================================
# Expressions as defined in Section 3.4 of the IR specification:

class Expression(JSONRepresentable):
    result_type : "Type"

class MethodInvocationExpression(Expression):
    target      : Expression
    method_name : str
    args        : List[Argument]

    def __init__(self, target: Expression, method_name, args: List[Argument]) -> None:
        if re.search(FUNC_NAME_REGEX, method_name) == None:
            raise TypeError("Invalid method name {}".format(method_name))
        if not self.is_invocation_valid(args, target, method_name):
        	raise TypeError("Invalid method invocation {}".format(method_name))        
        self.target      = target
        self.method_name = method_name
        self.args        = args
        self.result_type = target.result_type.get_method(method_name).return_type
        
    def is_invocation_valid(self, args: List[Argument], target: Expression, method_name: str) -> bool:
    	arg_types = {"self": target.result_type}
    	arg_types.update({arg.arg_name:arg.arg_type for arg in args})
    	param_types = {param.param_name:param.param_type for param in target.result_type.get_method(method_name).parameters}
    	return arg_types == param_types
    	
    def json_repr(self) -> Dict:
        return {"expression" : "MethodInvocation",
                "target"     : self.target,
                "method"     : self.method_name,
                "arguments"  : self.args}
		
class FunctionInvocationExpression(Expression):
    func : Function
    args : List[Argument]

    def __init__(self, func: Function, args: List[Argument]) -> None:
        if re.search(FUNC_NAME_REGEX, func.name) == None:
            raise TypeError("Invalid function name {}".format(func.name))
        self.func        = func
        self.args        = args
        self.result_type = func.return_type
        
    def json_repr(self) -> Dict:
        return {"expression" : "FunctionInvocation",
                "name"       : self.func.name,
                "arguments"  : self.args}

class FieldAccessExpression(Expression):
    """
    An expression representing access to `field` of `target`.
    The `target` must be a structure type.
    """
    target     : Expression
    field_name : str

    def __init__(self, target: Expression, field_name: str) -> None:
        if isinstance(target.result_type, Struct):
            self.target     = target
            self.field_name = field_name
            self.result_type  = target.result_type.field(field_name).field_type
        else:
            raise TypeError("Cannot access fields in object of type {}".format(target.result_type))
            
    def json_repr(self) -> Dict:
        return {"expression" : "FieldAccess",
                "target"     : self.target,
                "field"      : self.field}

class ContextAccessExpression(Expression):
    # FIXME: we need a Context object
    context    : Dict[str, "ContextField"]
    field_name : str

    def __init__(self, context: Dict[str, "ContextField"], field_name: str) -> None:
        self.context     = context
        self.field_name  = field_name
        self.result_type = self.context[self.field_name].field_type
        
    def json_repr(self) -> Dict:
        return {"expression" : "ContextAccess",
                "field"      : field_name}

class IfElseExpression(Expression):
    condition : Expression
    if_else   : Expression
    if_false  : Expression

    def __init__(self, condition: Expression, if_true: Expression, if_false: Expression) -> None:
        if condition.result_type.kind != "Boolean":
            raise TypeError("Cannot create IfElseExpression: condition is not boolean")
        if if_true.result_type != if_false.result_type:
            raise TypeError("Cannot create IfElseExpression: branch types differ")
        self.condition   = condition
        self.if_true     = if_true
        self.if_false    = if_false
        self.result_type = if_true.result_type
        
    def json_repr(self) -> Dict:
        return {"expression" : "IfElse",
                "condition"  : self.condition,
                "if_true"    : self.if_true,
                "if_false"   : self.if_false}

class ThisExpression(Expression):
    def __init__(self, this_type: "Type") -> None:
        self.result_type = this_type
        
    def json_repr(self) -> Dict:
        return {"expression" : This}

class ConstantExpression(Expression):
    result_type : "Type"
    value       : Any

    def __init__(self, constant_type: "Type", constant_value: Any) -> None:
        self.result_type = constant_type
        self.value       = constant_value
    
    def json_repr(self) -> Dict:
        return {"expression" : "Constant",
                "type"       : self.result_type,
                "value"      : self.value}
    