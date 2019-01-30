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

from typing import Dict, List, Tuple, Optional, Any, Union
from copy import deepcopy

import abc

import re

# Type names begin with an upper case letter, function names do not:
TYPE_NAME_REGEX = "^[A-Z][A-Za-z0-9$_]+$"
FUNC_NAME_REGEX = "^[a-z][A-Za-z0-9$_]+$"

# =================================================================================================
# JSONRepresentable abstract class

class JSONRepresentable(abc.ABC):

    @abc.abstractmethod
    def json_repr(self) -> Union[Dict, List, str, int, float, bool, None, "JSONRepresentable"]:
        pass

# =================================================================================================
# Type errors:

class TypeError(Exception):
    def __init__(self, reason):
        self.reason = reason

# =================================================================================================
# Functions, parameters, arguments, traits:

class Parameter(JSONRepresentable):
    param_name : str
    param_type : "Type"

    def __init__(self, param_name: str, param_type: "Type") -> None:
        self.param_name = param_name
        self.param_type = param_type

    def __eq__(self, other) -> bool:
        if not isinstance(other, Parameter):
            return False
        if self.param_name != other.param_name:
            return False
        if self.param_type != other.param_type:
            return False
        return True

    def is_self_param(self) -> bool:
        return (self.param_name == "self") and (self.param_type == None)
        
    def json_repr(self) -> Dict:
        return {"name" : self.param_name,
                "type" : self.param_type}

class Function(JSONRepresentable):
    name        : str
    parameters  : List[Parameter]
    return_type : "Type"

    def __init__(self, name: str, parameters: List[Parameter], return_type: "Type") -> None:
        self.name        = name
        self.parameters  = parameters
        self.return_type = return_type

    def is_method_compatible(self) -> bool:
        return self.parameters[0].is_self_param()
        
    def json_repr(self) -> Dict:
        return {"name"        : self.name,
                "parameters"  : self.parameters,
                "return_type" : self.return_type.name}

class Argument(JSONRepresentable):
    arg_name  : str
    arg_type  : "Type"
    arg_value : Any

    def __init__(self, arg_name: str, arg_type: "Type", arg_value: Any) -> None:
        self.arg_name  = arg_name
        self.arg_type  = arg_type
        self.arg_value = arg_value
        
    def json_repr(self) -> Dict:
        return {"name"  : self.arg_name,
                "value" : self.arg_value}

class Trait:
    name    : str
    methods : Dict[str, Function]

    def __init__(self, name: str, methods: List[Function]) -> None:
        self.name    = name
        self.methods = {}
        for method in methods:
            self.methods[method.name] = method

    def __str__(self):
        print("Trait<{}>".format(self.name))

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
                "field"      : self.field_name}

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
                "field"      : self.field_name}

class IfElseExpression(Expression):
    condition : Expression
    if_true   : Expression
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
        return {"expression" : "This"}

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

# =================================================================================================
# Fields in a structure or the context:

class Transform(JSONRepresentable):
    def __init__(self, into_name: str, into_type: "Type", using: Function) -> None:
        self.into_name = into_name
        self.into_type = into_type
        self.using     = using
        
    def json_repr(self) -> Dict:
        return {"into_name" : self.into_name,
                "into_type" : self.into_type.name,
                "using"     : self.using.name}

class StructField(JSONRepresentable):
    def __init__(self, 
                 field_name: str, 
                 field_type: "Type", 
                 is_present: Optional[Expression], 
                 transform : Optional[Transform]) -> None:
        self.field_name = field_name
        self.field_type = field_type
        self.is_present = is_present
        self.transform  = transform

    def json_repr(self) -> Dict:
        return {"name"       : self.field_name,
                "type"       : self.field_type.name,
                "is_present" : self.is_present,
                "transform"  : self.transform}

class ContextField(JSONRepresentable):
    def __init__(self, field_name: str, field_type: "Type") -> None:
        self.field_name = field_name
        self.field_type = field_type
        
    def json_repr(self) -> Dict:
        return {"name" : self.field_name,
                "type" : self.field_type.name}

# =================================================================================================
# Types:

class Type:
    kind:    str
    name:    str
    traits:  Dict[str,Trait]
    methods: Dict[str,Function]

    def __init__(self):
        self.kind    = None
        self.name    = None
        self.traits  = {}
        self.methods = {}

    def __str__(self):
        res = "Type<{}::{}".format(self.kind, self.name)
        for trait in self.traits:
            res += " " + trait
        res += ">"
        return res

    def __eq__(self, obj):
    	#FIXME: this is probably OK for now, but a deeper notion of equality would be better
        return self.name == obj.name

    def implement_trait(self, trait: Trait):
        if trait in self.traits:
            raise TypeError("Type {} already implements trait {}".format(self.name, trait.name))
        else:
            self.traits[trait.name] = trait
            for method_name in trait.methods:
                self.methods[method_name] = deepcopy(trait.methods[method_name])
            	# When a type implements a trait, any unspecified (None) types are set to
            	# the implementing type
                for parameter in self.methods[method_name].parameters:
                	if parameter.param_type is None:
                		parameter.param_type = self
                if self.methods[method_name].return_type is None:
                	self.methods[method_name].return_type = self

    def get_method(self, method_name) -> Function:
        return self.methods[method_name]

class Nothing(Type):
    def __init__(self):
        super().__init__()
        self.kind  = "Nothing"
        self.name  = "Nothing"

class Boolean(Type):
    def __init__(self):
        super().__init__()
        self.kind  = "Boolean"
        self.name  = "Boolean"

class Size(Type):
    def __init__(self):
        super().__init__()
        self.kind  = "Size"
        self.name  = "Size"

class BitString(Type):
    def __init__(self, name, size):
        super().__init__()
        self.kind = "BitString"
        self.name = name
        self.size = size

class Array(Type):
    def __init__(self, name, element_type, length):
        super().__init__()
        self.kind         = "Array"
        self.name         = name
        self.element_type = element_type
        self.length       = length
        if length == None or self.element_type.size == None:
            self.size = None
        else:
            self.size = self.length * self.element_type.size

class Struct(Type):
    kind:        str
    name:        str
    fields:      List[StructField]
    constraints: List[Expression]
    actions:     List[Expression]

    def __init__(self, name):
        super().__init__()
        self.kind        = "Struct"
        self.name        = name
        self.fields      = []
        self.constraints = []
        self.actions     = []

    def add_field(self, field: StructField):
        self.fields.append(field)

    def add_constraint(self, constraint: Expression):
        self.constraints.append(constraint)

    def add_action(self, action: Expression):
        self.actions.append(action)

    def field(self, field_name) -> StructField:
        for field in self.fields:
            if field.field_name == field_name:
                return field
        raise TypeError("{} has no field named {}".format(self.name, field_name))

class Enum(Type):
    def __init__(self, name, variants):
        super().__init__()
        self.kind     = "Enum"
        self.name     = name
        self.variants = variants

# =================================================================================================
# vim: set tw=0 ai:
