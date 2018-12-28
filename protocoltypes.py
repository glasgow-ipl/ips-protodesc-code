# =================================================================================================
# Copyright (C) 2018 University of Glasgow
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

from abc    import ABCMeta, abstractmethod
from typing import Dict, List, Tuple, Optional

import re

# Type names begin with an upper case letter, function names do not:
TYPE_NAME_REGEX = "^[A-Z][A-Za-z0-9$_]+$"
FUNC_NAME_REGEX = "^[a-z][A-Za-z0-9$_]+$"

# =================================================================================================
# Type errors:

class TypeError(Exception):
    def __init__(self, reason):
        self.reason = reason

# =================================================================================================
# Functions, parameters, arguments, traits:

class Parameter:
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

class Function:
    def __init__(self, name: str, parameters: List[Parameter], return_type: "Type") -> None:
        self.name        = name
        self.parameters  = parameters
        self.return_type = return_type

    def is_method_compatible(self):
        return self.parameters[0].is_self_param()

class Argument:
    def __init__(self, arg_name: str, arg_type: "Type", arg_value) -> None:
        self.name  = arg_name
        self.type  = arg_type
        self.value = arg_value

class Trait:
    name    : str
    methods : Dict[str,Function]

    def __init__(self, name: str, methods: List[Function]) -> None:
        self.name    = name
        self.methods = {}
        for method in methods:
            self.methods[method.name] = method

    def __str__(self):
        print("Trait<{}>".format(self.name))

# =================================================================================================
# Expressions as defined in Section 3.4 of the IR specification:

class Expression(metaclass=ABCMeta):
    @abstractmethod
    def type(self):
        pass

class MethodInvocationExpression(Expression):
    def __init__(self, target: Expression, method, args: List[Argument]) -> None:
        if re.search(FUNC_NAME_REGEX, method) == None:
            raise TypeError("Cannot create MethodInvocationExpression {}: malformed name".format(method))
        self.target = target
        self.method = method
        self.args   = args

    def type(self):
        target = self.target.type()
        method = target.get_method(self.method)
        return method.return_type

class FunctionInvocationExpression(Expression):
    def __init__(self, func: Function, args: List[Argument]) -> None:
        if re.search(FUNC_NAME_REGEX, func.name) == None:
            raise TypeError("Cannot create FunctionInvocationExpression {}: malformed name".format(func.name))
        self.func   = func
        self.args   = args

    def type(self):
        return self.func.return_type

class FieldAccessExpression(Expression):
    """
    An expression representing access to `field` of `target`.
    The `target` must be a structure type.
    """
    target : Expression
    field_name : str

    def __init__(self, target: Expression, field_name: str) -> None:
        if target.type().kind != "Struct":
            raise TypeError("Cannot access fields in object of type {}".format(target.type()))
        self.target     = target
        self.field_name = field_name

    def type(self):
        return self.target.type().get_field(self.field_name).type

class ContextAccessExpression(Expression):
    def __init__(self, context, field_name: str) -> None:
        self.context    = context
        self.field_name = field_name

    def type(self):
        return self.context[self.field_name].type

class IfElseExpression(Expression):
    condition : Expression
    if_else   : Expression
    if_false  : Expression

    def __init__(self, condition: Expression, if_true: Expression, if_false: Expression) -> None:
        if condition.type().kind != "Boolean":
            raise TypeError("Cannot create IfElseExpression: condition is not boolean")
        if if_true.type() != if_false.type():
            raise TypeError("Cannot create IfElseExpression: branch types differ")
        self.condition = condition
        self.if_true   = if_true
        self.if_false  = if_false

    def type(self):
        return self.if_true.type()

class ThisExpression(Expression):
    def __init__(self, this):
        self.this = this

    def type(self):
        return self.this

class ConstantExpression(Expression):
    def __init__(self, constant_type, constant_value):
        self._type = constant_type
        self.value = constant_value

    def type(self):
        return self._type

# =================================================================================================
# Fields in a structure or the context:

class Transform:
    def __init__(self, into_name: str, into_type: "Type", using: Function) -> None:
        self.into_name = into_name
        self.into_type = into_type
        self.using     = using

class StructField:
    def __init__(self, field_name: str, field_type: "Type", is_present: Optional[Expression], transform: Optional[Transform]) -> None:
        self.name       = field_name
        self.type       = field_type
        self.is_present = is_present
        self.transform  = transform

    def __str__(self):
        return "StructField<{},{},{},{}>".format(self.name, self.type, self.is_present, self.transform)

class ContextField:
    def __init__(self, field_name: str, field_type: "Type") -> None:
        self.name       = field_name
        self.type       = field_type

    def __str__(self):
        return "ContextField<{},{}>".format(self.name, self.type)

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

    def implement_trait(self, trait: Trait):
        if trait in self.traits:
            raise TypeError("Cannot implement trait {} for type {}: already implemented".format(trait.name, self.name))
        else:
            self.traits[trait.name] = trait
            for method_name in trait.methods:
                self.methods[method_name] = trait.methods[method_name]

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
        if length == None:
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

    def get_field(self, field_name) -> Optional[StructField]:
        for field in self.fields:
            if field.name == field_name:
                return field
        return None

class Enum(Type):
    def __init__(self, name, variants):
        super().__init__()
        self.kind     = "Enum"
        self.name     = name
        self.variants = variants

# =================================================================================================
# vim: set tw=0 ai:
