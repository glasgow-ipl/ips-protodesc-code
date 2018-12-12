# =================================================================================================
# Copyright (C) 2018 University of Glasgow
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
# =================================================================================================

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

class Function:
    def __init__(self, name, parameters, return_type):
        self.name        = name
        self.parameters  = parameters
        self.return_type = return_type

    def is_method_compatible(self):
        return self.parameters[0].name == "self"
        return self.parameters[0].type == None

class Parameter:
    def __init__(self, name_, type_):
        self.name = name_
        self.type = type_

class Argument:
    def __init__(self, name_, type_, value_):
        self.name  = name_
        self.type  = type_
        self.value = value_

class Trait:
    def __init__(self, name, methods: List[Function]) -> None:
        self.name    = name
        self.methods = methods

    def __str__(self):
        print("Trait<{}>".format(self.name))

# =================================================================================================
# Expressions as defined in Section 3.4 of the IR specification:

class Expression:
    def type(self):
        raise TypeError("Expression::type() must be implemented by subclasses")

class MethodInvocationExpression(Expression):
    def __init__(self, target: Expression, method, args: List[Argument]) -> None:
        if re.search(FUNC_NAME_REGEX, method) == None:
            raise TypeError("Cannot create expression {}: malformed method name".format(method))
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
            raise TypeError("Cannot create expression {}: malformed function name".format(func.name))
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
    field  : str

    def __init__(self, target, field):
        if target.type().kind != "Struct":
            raise TypeError("Cannot access field of object with type {}".format(target.type()))
        self.target = target
        self.field  = field

    def type(self):
        target = self.target.type()
        field  = target.get_field(self.field)
        return field.type

class ContextAccessExpression(Expression):
    def __init__(self, field):
        self.field = field

    def type(self):
        # FIXME: implement this
        raise TypeError("unimplemented (ContextAccessExpression::type)")

class IfElseExpression(Expression):
    def __init__(self, condition: Expression, if_true: Expression, if_false: Expression) -> None:
        self.condition = condition
        self.if_true   = if_true
        self.if_false  = if_false
        if if_true.type() != if_false.type():
            raise TypeError("Cannot create expression: IfElse branch types differ")
        #if condition.type() != self.get_type["Boolean"]:
        #    raise TypeError("Cannot create expression: IfElse condition not Boolean")

    def type(self):
        return self.if_true.type()

class ThisExpression(Expression):
    def __init__(self, this):
        self._this = this

    def type(self):
        return self._this

class ConstantExpression(Expression):
    def __init__(self, type_, value):
        self.type_ = type_
        self.value = value

    def type(self):
        return self.type_

# =================================================================================================
# Fields in a structure or the context:

class Transform:
    def __init__(self, into_name, into_type, using):
        self.into_name = into_name
        self.into_type = into_type
        self.using     = using

class Field:
    def __init__(self, name_, type_, is_present_: Optional[Expression], transform_: Optional[Transform]) -> None:
        self.name       = name_
        self.type       = type_
        self.is_present = is_present_
        self.transform  = transform_

    def __str__(self):
        return "Field<{},{},{},{}>".format(self.name, self.type, self.is_present, self.transform)

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
        return "Type<{}::{}>".format(self.kind, self.name)

    def implement_trait(self, trait: Trait):
        if trait in self.traits:
            raise TypeError("Cannot implement trait {} for type {}: already implemented".format(trait.name, self.name))
        else:
            self.traits[trait.name] = trait
            for method in trait.methods:
                if method.name in self.methods:
                    raise TypeError("Cannot add method {} for type {}: already implemented".format(method.name, self.name))
                else:
                    self.methods[method.name] = method

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
    fields:      List[Field]
    constraints: List[Expression]
    actions:     List[Expression]

    def __init__(self, name):
        super().__init__()
        self.kind        = "Struct"
        self.name        = name
        self.fields      = []
        self.constraints = []
        self.actions     = []

    def add_field(self, field: Field):
        self.fields.append(field)

    def add_constraint(self, constraint: Expression):
        self.constraints.append(constraint)

    def add_action(self, action: Expression):
        self.actions.append(action)

    def get_field(self, field_name) -> Optional[Field]:
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
