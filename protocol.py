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

from abc         import ABC, abstractmethod
from dataclasses import dataclass
from copy        import copy, deepcopy
from typing      import Dict, List, Any, Optional, cast

import unittest
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

@dataclass(frozen=True)
class Parameter:
    param_name : str
    param_type : "ProtocolType"


@dataclass(frozen=True)
class Argument:
    arg_name  : str
    arg_type  : "ProtocolType"
    arg_value : Any


@dataclass(frozen=True)
class Function:
    name        : str
    parameters  : List[Parameter]
    return_type : "ProtocolType"

    def is_method(self, self_type: "ProtocolType") -> bool:
        if self.parameters[0].param_name != "self":
            return False
        if self.parameters[0].param_type != self_type:
            return False
        return True


    def is_method_accepting(self, self_type:"ProtocolType", arguments:List[Argument]) -> bool:
        """
        Check if this function is a method and accepts the specified arguments when invoked on an
        object of type self_type
        """
        if not self.is_method(self_type):
            return False
        for (p, a) in zip(self.parameters[1:], arguments):
            pname = p.param_name
            ptype = p.param_type if p.param_type is not None else self_type
            if (pname != a.arg_name):
                return False
            if (ptype != a.arg_type) and not a.arg_type.is_a(ptype):
                return False
        return True


@dataclass(frozen=True)
class Trait:
    name    : str
    methods : List[Function]


# =================================================================================================
# Expressions as defined in Section 3.4 of the IR specification:

class Expression(ABC):
    @abstractmethod
    def get_result_type(self, containing_type: "ProtocolType") -> "ProtocolType":
        raise ProtocolTypeError("Expression MUST be subclassed")


@dataclass(frozen=True)
class ArgumentExpression(Expression):
    arg_name: str
    arg_value: Expression

    def get_result_type(self, containing_type: "ProtocolType") -> "ProtocolType":
        return self.arg_value.get_result_type(containing_type)


@dataclass(frozen=True)
class MethodInvocationExpression(Expression):
    target      : Expression
    method_name : str
    arg_exprs   : List[ArgumentExpression]

    def __post_init__(self):
        if re.search(FUNC_NAME_REGEX, self.method_name) == None:
            raise ProtocolTypeError("Method {}: invalid name".format(self.method_name))

    def get_result_type(self, containing_type: "ProtocolType") -> "ProtocolType":
        args   = [Argument(arg.arg_name, arg.get_result_type(containing_type), arg.arg_value) for arg in self.arg_exprs]
        result = self.target.get_result_type(containing_type)
        method = result.get_method(self.method_name) 
        if not method.is_method_accepting(result, args):
            raise ProtocolTypeError("Method {}: invalid arguments".format(self.method_name))
        return method.return_type


@dataclass(frozen=True)
class FunctionInvocationExpression(Expression):
    func       : Function
    args_exprs : List[ArgumentExpression]

    def __psto_init__(self):
        if re.search(FUNC_NAME_REGEX, self.func.name) == None:
            raise ProtocolTypeError("Invalid function name {}".format(self.func.name))

    def get_result_type(self, containing_type: "ProtocolType") -> "ProtocolType":
        return self.func.return_type


@dataclass(frozen=True)
class FieldAccessExpression(Expression):
    """
    An expression representing access to `field` of `target`.
    The `target` must be a structure type.
    """
    target     : Expression
    field_name : str

    def get_result_type(self, containing_type: "ProtocolType") -> "ProtocolType":
        if isinstance(self.target.get_result_type(containing_type), Struct):
            struct = cast(Struct, self.target.get_result_type(containing_type))
            return struct.field(self.field_name).field_type
        else:
            raise ProtocolTypeError("Cannot access fields in object of type {}".format(self.target.get_result_type(containing_type)))


@dataclass(frozen=True)
class ContextAccessExpression(Expression):
    context    : "Context"
    field_name : str

    def get_result_type(self, containing_type: "ProtocolType") -> "ProtocolType":
        return self.context.field(self.field_name).field_type


@dataclass(frozen=True)
class IfElseExpression(Expression):
    condition : Expression
    if_true   : Expression
    if_false  : Expression

    def get_result_type(self, containing_type: "ProtocolType") -> "ProtocolType":
        if self.condition.get_result_type(containing_type).kind != "Boolean":
            raise ProtocolTypeError("Cannot create IfElseExpression: condition is not boolean")
        if self.if_true.get_result_type(containing_type) != self.if_false.get_result_type(containing_type):
            raise ProtocolTypeError("Cannot create IfElseExpression: branch types differ")
        return self.if_true.get_result_type(containing_type)


@dataclass(frozen=True)
class SelfExpression(Expression):
    def get_result_type(self, containing_type: "ProtocolType") -> "ProtocolType":
        return containing_type


@dataclass(frozen=True)
class ConstantExpression(Expression):
    constant_type  : "ProtocolType"
    constant_value : Any

    def get_result_type(self, containing_type: "ProtocolType") -> "ProtocolType":
        return self.constant_type


# =================================================================================================
# Fields in a structure or the context:

@dataclass(frozen=True)
class StructField():
    field_name: str
    field_type: "ProtocolType"
    is_present: Optional[Expression]


@dataclass(frozen=True)
class ContextField():
    field_name : str
    field_type : "ProtocolType"


# =================================================================================================
# Protocol Types:

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
    parent:  Optional["ProtocolType"]
    traits:  Dict[str,Trait]
    methods: Dict[str,Function]

    def __init__(self, parent) -> None:
        # self.kind and self.name are initialised by subtypes
        self.traits  = {}
        self.methods = {}
        self.parent  = parent

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
#        if self.traits != obj.traits:
#            return False
#        if self.methods != obj.methods:
#            return False
        return True
        
    def is_a(self, obj):
        parents = []
        while self.parent != None:
            parents.append(self.parent)
            self = self.parent
        return obj in parents

    def implement_trait(self, trait: Trait) -> None:
        if trait.name in self.traits:
            raise ProtocolTypeError("Type {} already implements trait {}".format(self.name, trait.name))
        else:
            self.traits[trait.name] = trait
            for method in trait.methods:
                if method.name in self.methods:
                    raise ProtocolTypeError("Type {} already implements method {}".format(self.name, method.name))
                else:
                    mf_name        = method.name
                    mf_return_type = method.return_type if method.return_type is not None else self
                    mf_parameters  = []
                    for p in method.parameters:
                        pn = p.param_name
                        pt = p.param_type if p.param_type is not None else self
                        mf_parameters.append(Parameter(pn, pt))
                    self.methods[method.name] = Function(mf_name, mf_parameters, mf_return_type)

    def get_method(self, method_name) -> Function:
        # try to get the method in the narrowest type, but traverse chain of parent types
        method = None
        current_type = self
        while method is None:
            method = current_type.methods.get(method_name, None)
            if current_type.parent is not None:
                current_type = current_type.parent
            else: 
                break
        if method is None:
            raise ProtocolTypeError("{} and its parents do not implement the {} method".format(self.name, method_name))
        return method

# Internal types follow:

#FIXME: need to think about the purpose of these types: should they hold values?
class Boolean(ProtocolType):
    def __init__(self) -> None:
        super().__init__(None)
        self.kind  = "Boolean"
        self.name  = "Boolean"


class Number(ProtocolType):
    def __init__(self) -> None:
        super().__init__(None)
        self.kind  = "Number"
        self.name  = "Number"


class Nothing(ProtocolType):
    def __init__(self) -> None:
        super().__init__(None)
        self.kind  = "Nothing"
        self.name  = "Nothing"
        self.size = 0

# Representable types follow:

class BitString(ProtocolType):
    size : Optional[int]

    def __init__(self, name: str, size: Optional[int]) -> None:
        super().__init__(None)
        self.kind = "BitString"
        self.name = name
        self.size = size


class Option(ProtocolType):
    def __init__(self, name: str, reference_type: ProtocolType) -> None:
        super().__init__(None)
        self.kind = "Option"
        self.name = name
        self.reference_type = ProtocolType
        self.size = reference_type.size


class Array(ProtocolType):
    element_type : ProtocolType
    length       : Optional[int]

    def __init__(self, name: str, element_type: ProtocolType, length: Optional[int]) -> None:
        super().__init__(None)
        self.kind         = "Array"
        self.name         = name
        self.element_type = element_type
        self.length       = length

        if length == None:
            self.size = None
        elif isinstance(self.element_type, BitString):
            element_bitstring = self.element_type
            if element_bitstring.size is None or self.length is None:
                self.size = None
            else:
                self.size = self.length * element_bitstring.size
        elif isinstance(self.element_type, Array):
            element_array = self.element_type
            if element_array.size is None or self.length is None:
                self.size = None
            else:
                self.size = self.length * element_array.size


class Struct(ProtocolType):
    fields:      List[StructField]
    constraints: List[Expression]
    actions:     List[Expression]

    def __init__(self, name: str) -> None:
        super().__init__(None)
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
    variants : List[ProtocolType]

    def __init__(self, name: str, variants: List[ProtocolType]) -> None:
        super().__init__(None)
        self.kind     = "Enum"
        self.name     = name
        self.variants = variants


class Context(ProtocolType):
    fields: List[ContextField]

    def __init__(self) -> None:
        super().__init__(None)
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

class Protocol:
    _name   : str
    _types  : Dict[str,ProtocolType]
    _traits : Dict[str,Trait]
    _funcs  : Dict[str,Function]
    _context: Context
    _pdus   : Dict[str,ProtocolType]

    def __init__(self):
        # The protocol is initially unnammed:
        self._name  = None
        # Define the primitive types:
        self._types = {}
        self._types["Nothing"] = Nothing()
        self._types["Boolean"] = Boolean()
        self._types["Number"] = Number()
        
        # Define the standard traits:
        self._traits = {}
        self._traits["Value"] = Trait("Value", [
            Function("get", [Parameter("self", None)], None),
            Function("set", [Parameter("self", None), Parameter("value", None)], self.get_type("Nothing"))
        ])
        self._traits["Sized"] = Trait("Sized", [
            Function("size", [Parameter("self", None)], self.get_type("Number"))
        ])
        self._traits["IndexCollection"] = Trait("IndexCollection", [
            Function("get",    [Parameter("self", None), Parameter("index", self.get_type("Number"))], None),
            Function("set",    [Parameter("self", None), Parameter("index", self.get_type("Number")), Parameter("value", None)], self.get_type("Nothing")),
            Function("length", [Parameter("self", None)], self.get_type("Number"))
        ])
        self._traits["Equality"] = Trait("Equality", [
            Function("eq", [Parameter("self", None), Parameter("other", None)], self.get_type("Boolean")),
            Function("ne", [Parameter("self", None), Parameter("other", None)], self.get_type("Boolean"))
        ])
        self._traits["Ordinal"] = Trait("Ordinal", [
            Function("lt", [Parameter("self", None), Parameter("other", None)], self.get_type("Boolean")),
            Function("le", [Parameter("self", None), Parameter("other", None)], self.get_type("Boolean")),
            Function("gt", [Parameter("self", None), Parameter("other", None)], self.get_type("Boolean")),
            Function("ge", [Parameter("self", None), Parameter("other", None)], self.get_type("Boolean"))
        ])
        self._traits["BooleanOps"] = Trait("BooleanOps", [
            Function("and", [Parameter("self", None), Parameter("other", None)], self.get_type("Boolean")),
            Function("or",  [Parameter("self", None), Parameter("other", None)], self.get_type("Boolean")),
            Function("not", [Parameter("self", None)], self.get_type("Boolean"))
        ])
        self._traits["ArithmeticOps"] = Trait("ArithmeticOps", [
            Function("plus",    [Parameter("self", None), Parameter("other", None)], None),
            Function("minus",   [Parameter("self", None), Parameter("other", None)], None),
            Function("multiply",[Parameter("self", None), Parameter("other", None)], None),
            Function("divide",  [Parameter("self", None), Parameter("other", None)], None),
            Function("modulo",  [Parameter("self", None), Parameter("other", None)], None)
        ])
        self._traits["NumberRepresentable"] = Trait("NumberRepresentable", [
            Function("to_number", [Parameter("self", None)], self.get_type("Number"))
        ])
        # Implement standard traits:
        self._types["Boolean"].implement_trait(self.get_trait("Value"))
        self._types["Boolean"].implement_trait(self.get_trait("Equality"))
        self._types["Boolean"].implement_trait(self.get_trait("BooleanOps"))
        self._types["Number"].implement_trait(self.get_trait("Value"))
        self._types["Number"].implement_trait(self.get_trait("Equality"))
        self._types["Number"].implement_trait(self.get_trait("Ordinal"))
        self._types["Number"].implement_trait(self.get_trait("ArithmeticOps"))
        self._types["Nothing"].implement_trait(self.get_trait("Sized"))
        # Define the standard functions:
        self._funcs = {}
        # Define the context:
        self._context = Context()
        # Define the PDUs:
        self._pdus = {}

    # =============================================================================================
    # Private helper functions:

    def _validate_typename(self, name:str):
        if name in self._types:
            raise ProtocolTypeError("Cannot create type {}: already exists".format(name))
        if re.search(TYPE_NAME_REGEX, name) is None:
            raise ProtocolTypeError("Cannot create type {}: malformed name".format(name))

    def _validate_fields(self, fields:List[StructField]):
        for field in fields:
            if re.search(FUNC_NAME_REGEX, field.field_name) is None:
                raise ProtocolTypeError("Cannot parse field {}: malformed name".format(field.field_name))
        return fields

    def _validate_constraints(self, struct:Struct, constraints:List[Expression]):
        for constraint in constraints:
            if constraint.get_result_type(struct) != self.get_type("Boolean"):
                raise ProtocolTypeError("Cannot parse constraint: {} != Boolean".format(constraint.get_result_type(struct)))
        return constraints

    def _validate_actions(self, struct:Struct, actions:List[Expression]):
        for action in actions:
            if action.get_result_type(struct) != self.get_type("Nothing"):
                raise ProtocolTypeError("Cannot parse actions: returns {} not Nothing".format(action.get_result_type(struct)))
        return actions

    # =============================================================================================
    # Public API:

    def set_protocol_name(self, name: str) -> None:
        """
        Define the name of the protocol.

        Parameters:
            self - the protocol in which the new type is defined
            name - the name of the protocol
        """
        if self._name != None:
            raise ProtocolTypeError("Cannot redefine protocol name")
        self._name = name

    def define_bitstring(self, name:str, size:Optional[int]) -> BitString:
        """
        Define a new bit string type for this protocol.

        Parameters:
          self  - the protocol in which the new type is defined
          name  - the name of the new type
          size  - the size of the new type, in bits. None if variable
        """
        self._validate_typename(name)
        newtype = BitString(name, size)
        newtype.implement_trait(self.get_trait("Sized"))
        newtype.implement_trait(self.get_trait("Value"))
        newtype.implement_trait(self.get_trait("Equality"))
        newtype.implement_trait(self.get_trait("NumberRepresentable"))
        self._types[name] = newtype
        return newtype

    def define_option(self, name:str, reference_type:ProtocolType) -> Option:
        """
        Define a new option type for this protocol.

        Parameters:
          self  - the protocol in which the new type is defined
          name  - the name of the new type
          reference_type - the type which this instantiation of Option will take (either Nothing or another representable type)
          size  - the size of reference_type (0 if Nothing, varies for other representable types)
        """
        self._validate_typename(name)
        newtype = Option(name, reference_type)
        newtype.implement_trait(self.get_trait("Sized"))
        self._types[name] = newtype
        return newtype

    def define_array(self, name:str, element_type: ProtocolType, length: Optional[int]) -> Array:
        """
        Define a new array type for this protocol.

        Parameters:
          self  - the protocol in which the new type is defined
          name  - the name of the new type
          element_type - a Type object, representing the element type
          length - the number of elements in the array
        """
        self._validate_typename(name)
        newtype = Array(name, element_type, length)
        newtype.implement_trait(self.get_trait("Sized"))
        newtype.implement_trait(self.get_trait("Equality"))
        newtype.implement_trait(self.get_trait("IndexCollection"))
        self._types[name] = newtype
        return newtype

    def define_struct(self, name:str, fields:List[StructField], constraints:List[Expression], actions:List[Expression]) -> Struct:
        """
        Define a new structure type for this protocol.

        Parameters:
          self        - the protocol in which the new type is defined
          name        - the name of the new type
          fields      - the fields that are in the struct
          constraints - the constraints to define in the struct
          actions     - the action to define in the struct
        """
        newtype = Struct(name)
        self._types[name] = newtype
        for field in self._validate_fields(fields):
            newtype.add_field(field)
        for constraint in self._validate_constraints(newtype, constraints):
            newtype.add_constraint(constraint)
        for action in self._validate_actions(newtype, actions):
            newtype.add_action(action)
        newtype.implement_trait(self.get_trait("Sized"))
        newtype.implement_trait(self.get_trait("Equality"))
        return newtype

    def define_enum(self, name:str, variants: List[ProtocolType]) -> Enum:
        """
        Define a new enumerated type for this protocol.

        Parameters:
          self     - the protocol in which the new type is defined
          name     - the name of the new type
          variants - the variant types of the enum
        """
        self._validate_typename(name)
        newtype = Enum(name, variants)
        newtype.implement_trait(self.get_trait("Sized"))
        self._types[name] = newtype
        return newtype

    def derive_type(self, name: str, derived_from: ProtocolType, also_implements: List[Trait]) -> ProtocolType:
        """
        Define a new derived type for this protocol.
        The type constructor is described in Section 3.3.5 of the IR specification.

        Parameters:
          self            - the protocol in which the new type is defined
          name            - the name of the new type
          derived_from    - the type that the new type is derived from
          also_implements - additional traits that are implemented
        """
        self._validate_typename(name)
        self._types[name] = copy(derived_from)
        self._types[name].name    = name
        self._types[name].methods = copy(derived_from.methods)
        for trait in also_implements:
            self._types[name].implement_trait(trait)
        return self._types[name]

    def define_function(self, name:str, parameters:List[Parameter], return_type:ProtocolType) -> Function:
        """
        Define a new function type for this protocol.

        Parameters:
          self        - the protocol in which the new type is defined
          name        - the name of the new function
          return_type - the type that the function returns
        """
        if name in self._funcs:
            raise ProtocolTypeError("Cannot create Function {}: already exists".format(name))
        if re.search(FUNC_NAME_REGEX, name) is None:
            raise ProtocolTypeError("Cannot create Function {}: malformed name".format(name))
        newfunc = Function(name, parameters, return_type)
        self._funcs[name] = newfunc
        return newfunc

    def define_context_field(self, name:str, ptype:ProtocolType):
        """
        Define a context field for this protocol.

        Parameters:
          self   - the protocol whose context is to be added to
          field  - the field to be added
        """
        self._context.add_field(ContextField(name, ptype))

    def define_pdu(self, pdu: str) -> None:
        """
        Define a PDU for this protocol.

        Parameters:
          self  - the protocol in which the new type is defined
          pdu   - the name of a pre-existing type that is a PDU
        """
        self._pdus[pdu] = self.get_type(pdu)

    def get_protocol_name(self) -> str:
        return self._name

    def has_type(self, type_name: str) -> bool:
        return type_name in self._types

    def get_type(self, type_name: str) -> ProtocolType:
        return self._types[type_name]

    def get_func(self, func_name: str) -> Function:
        return self._funcs[func_name]

    def get_trait(self, trait_name: str) -> Trait:
        return self._traits[trait_name]

    def get_context(self):
        return self._context

    def get_pdu(self, pdu_name: str) -> ProtocolType:
        return self._pdus[pdu_name]

    def get_pdu_names(self) -> List[str]:
        return list(self._pdus.keys())

    def get_type_names(self) -> List[str]:
        return list(self._types.keys())

# vim: set tw=0 ai:
