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

from typing import Dict, List, Any, Optional, cast

from abc import ABC

import re

# Type names begin with an upper case letter, function names do not:
TYPE_NAME_REGEX = "^[A-Z][A-Za-z0-9$_]+$"
FUNC_NAME_REGEX = "^[a-z][A-Za-z0-9$_]+$"

# =================================================================================================
# Type errors:

class ProtocolTypeError(Exception):
    def __init__(self, reason):
        self.reason = reason


# =================================================================================================
# Parameters, arguments, functions, and traits:

class Parameter():
    param_name : str
    param_type : "ProtocolType"

    def __init__(self, param_name: str, param_type: "ProtocolType") -> None:
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


class Argument():
    arg_name  : str
    arg_type  : "ProtocolType"
    arg_value : Any

    def __init__(self, arg_name: str, arg_type: "ProtocolType", arg_value: Any) -> None:
        self.arg_name  = arg_name
        self.arg_type  = arg_type
        self.arg_value = arg_value


class Function():
    name        : str
    parameters  : List[Parameter]
    return_type : "ProtocolType"

    def __init__(self, name: str, parameters: List[Parameter], return_type: "ProtocolType") -> None:
        self.name        = name
        self.parameters  = parameters
        self.return_type = return_type

    def is_method_compatible(self) -> bool:
        return self.parameters[0].is_self_param()

    def method_accepts_arguments(self, self_type, arguments:List["Argument"]) -> bool:
        # Returns True if the arguments match the parameters of this function,
        # and this function is method compatible.
        if not self.is_method_compatible():
            return False
        for (p, a) in zip(self.parameters[1:], arguments):
            # if the method's parameter's type is None, then substitute it for the type of `self`
            if p.param_type is None:
                param_type = self_type
            else:
                param_type = p.param_type
            
            # check parameter names/types match argument names/types
            if p.param_name != a.arg_name:
                print("accepts_arguments: name mismatch {} vs {}".format(p.param_name, a.arg_name))
                return False
            if param_type != a.arg_type:
                print("accepts_arguments: type mismatch {} vs {}".format(param_type, a.arg_type))
                return False
        return True


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

class Expression():
    result_type : "ProtocolType"


class MethodInvocationExpression(Expression):
    target      : Expression
    method_name : str
    args        : List[Argument]

    def __init__(self, target: Expression, method_name:str, args: List[Argument]) -> None:
        if re.search(FUNC_NAME_REGEX, method_name) == None:
            raise ProtocolTypeError("Method {}: invalid name".format(method_name))
        if not target.result_type.get_method(method_name).method_accepts_arguments(target.result_type, args):
            raise ProtocolTypeError("Method {}: invalid arguments".format(method_name))
        self.target      = target
        self.method_name = method_name
        self.args        = args
        self.result_type = target.result_type.get_method(method_name).return_type


class FunctionInvocationExpression(Expression):
    func : Function
    args : List[Argument]

    def __init__(self, func: Function, args: List[Argument]) -> None:
        if re.search(FUNC_NAME_REGEX, func.name) == None:
            raise ProtocolTypeError("Invalid function name {}".format(func.name))
        self.func        = func
        self.args        = args
        self.result_type = func.return_type


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
            raise ProtocolTypeError("Cannot access fields in object of type {}".format(target.result_type))
            

class ContextAccessExpression(Expression):
    context    : "Context"
    field_name : str

    def __init__(self, context:"Context", field_name: str) -> None:
        self.context     = context
        self.field_name  = field_name
        self.result_type = self.context.field(field_name).field_type


class IfElseExpression(Expression):
    condition : Expression
    if_true   : Expression
    if_false  : Expression

    def __init__(self, condition: Expression, if_true: Expression, if_false: Expression) -> None:
        if condition.result_type.kind != "Boolean":
            raise ProtocolTypeError("Cannot create IfElseExpression: condition is not boolean")
        if if_true.result_type != if_false.result_type:
            raise ProtocolTypeError("Cannot create IfElseExpression: branch types differ")
        self.condition   = condition
        self.if_true     = if_true
        self.if_false    = if_false
        self.result_type = if_true.result_type
        

class ThisExpression(Expression):
    def __init__(self, this_type: "ProtocolType") -> None:
        self.result_type = this_type
        

class ConstantExpression(Expression):
    result_type : "ProtocolType"
    value       : Any

    def __init__(self, constant_type: "ProtocolType", constant_value: Any) -> None:
        self.result_type = constant_type
        self.value       = constant_value
    

# =================================================================================================
# Fields in a structure or the context:

class Transform():
    def __init__(self, into_name: str, into_type: "ProtocolType", using: Function) -> None:
        self.into_name = into_name
        self.into_type = into_type
        self.using     = using
        

class StructField():
    def __init__(self, 
                 field_name: str, 
                 field_type: "ProtocolType", 
                 is_present: Optional[Expression], 
                 transform : Optional[Transform]) -> None:
        self.field_name = field_name
        self.field_type = field_type
        self.is_present = is_present
        self.transform  = transform


class ContextField():
    def __init__(self, field_name: str, field_type: "ProtocolType") -> None:
        self.field_name = field_name
        self.field_type = field_type
        

# =================================================================================================
# Types:

class ProtocolType(ABC):
    """
    Types exist in the context of a Protocol. 
    The only valid way to create an object of class Type, or one of its subclasses,
    is by calling one of the following methods on a Protocol object:
     - define_bitstring()
     - define_array()
     - define_struct()
     - define_enum()
     - derive_type()
    The get_type() method of the Protocol object can be used to retrieve a reference
    to a pre-existing Type, given the type name.
    """

    kind:    str
    name:    str
    traits:  Dict[str,Trait]
    methods: Dict[str,Function]

    def __init__(self) -> None:
        # self.kind and self.name are initialised by subtypes
        self.traits  = {}
        self.methods = {}

    def __str__(self):
        res = "Type<{}::{}".format(self.kind, self.name)
        for trait in self.traits:
            res += " " + trait
        res += ">"
        return res

    def __eq__(self, obj):
        if type(self) != type(obj):
            return False
        if self.name != obj.name:
            return False
        if self.kind != obj.kind:
            return False
        if self.traits != obj.traits:
            return False
        if self.methods != obj.methods:
            return False
        return True

    def implement_trait(self, trait: Trait) -> None:
        if trait in self.traits:
            raise ProtocolTypeError("Type {} already implements trait {}".format(self.name, trait.name))
        else:
            self.traits[trait.name] = trait
            for method_name in trait.methods:
                if method_name in self.methods:
                    raise ProtocolTypeError("Type {} already implements method {}".format(self.name, method_name))
                else:
                    self.methods[method_name] = trait.methods[method_name]

    def get_method(self, method_name) -> Function:
        return self.methods[method_name]

#FIXME: need to think about the purpose of these types: should they hold values?
class Nothing(ProtocolType):
    def __init__(self) -> None:
        super().__init__()
        self.kind  = "Nothing"
        self.name  = "Nothing"


class Boolean(ProtocolType):
    def __init__(self) -> None:
        super().__init__()
        self.kind  = "Boolean"
        self.name  = "Boolean"


class Size(ProtocolType):
    def __init__(self) -> None:
        super().__init__()
        self.kind  = "Size"
        self.name  = "Size"


class BitString(ProtocolType):
    def __init__(self, name: str, size: int) -> None:
        super().__init__()
        self.kind = "BitString"
        self.name = name
        self.size = size


class Array(ProtocolType):
    def __init__(self, name: str, element_type: ProtocolType, length: int) -> None:
        super().__init__()
        self.kind         = "Array"
        self.name         = name
        self.element_type = element_type
        self.length       = length

        if length == None:
            self.size = None
        elif type(self.element_type) is BitString:
            element_bitstring = cast(BitString, self.element_type)
            if element_bitstring.size is None:
                self.size = None
            else:
                self.size = self.length * element_bitstring.size
        elif type(self.element_type) is Array:
            element_array = cast(Array, self.element_type)
            if element_array.size is None:
                self.size = None
            else:
                self.size = self.length * element_array.size


class Struct(ProtocolType):
    kind:        str
    name:        str
    fields:      List[StructField]
    constraints: List[Expression]
    actions:     List[Expression]

    def __init__(self, name: str) -> None:
        super().__init__()
        self.kind        = "Struct"
        self.name        = name
        self.fields      = []
        self.constraints = []
        self.actions     = []

    def add_field(self, field: StructField) -> None:
        self.fields.append(field)

    def add_constraint(self, constraint: Expression) -> None:
        self.constraints.append(constraint)

    def add_action(self, action: Expression) -> None:
        self.actions.append(action)

    def field(self, field_name: str) -> StructField:
        for field in self.fields:
            if field.field_name == field_name:
                return field
        raise ProtocolTypeError("{} has no field named {}".format(self.name, field_name))


class Enum(ProtocolType):
    def __init__(self, name: str, variants: List[ProtocolType]) -> None:
        super().__init__()
        self.kind     = "Enum"
        self.name     = name
        self.variants = variants


class Context(ProtocolType):
    kind:   str
    fields: List[ContextField]
    
    def __init__(self) -> None:
        super().__init__()
        self.kind   = "Context"
        self.fields = []
        
    def add_field(self, field: ContextField) -> None:
        self.fields.append(field)
        
    def field(self, field_name:str) -> ContextField:
        for field in self.fields:
            if field.field_name == field_name:
                return field
        raise ProtocolTypeError("Context has no field named {}".format(field_name))
        
# =================================================================================================
# vim: set tw=0 ai:
