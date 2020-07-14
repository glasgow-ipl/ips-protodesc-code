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

from abc         import ABC, abstractmethod
from dataclasses import dataclass
from copy        import copy, deepcopy
from typing      import Dict, List, Any, Optional, cast, Union

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
# Singleton metaclass:

class Singleton(type):
    _instances : Dict["Singleton", "Singleton"] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
            cls._instances[cls].__post_init__()
        return cls._instances[cls]
    
    def __post_init__(self):
        pass

# =================================================================================================
# Traits:

@dataclass(frozen=True)
class Trait(metaclass=Singleton):
    name    : str
    methods : List["Function"]

    def __post_init__(self):
        pass


class ValueTrait(Trait):
    def __init__(self):
        super().__init__("Value", [
            Function("get", [Parameter("self", None)], None),
            Function("set", [Parameter("self", None), Parameter("value", None)], Nothing())
        ])


class SizedTrait(Trait):
    def __init__(self):
        super().__init__("Sized", [
            Function("size", [Parameter("self", None)], Number())
        ])


class IndexCollectionTrait(Trait):
    def __init__(self):
        super().__init__("IndexCollection", [
            Function("get",    [Parameter("self", None), Parameter("index", Number())], None),
            Function("set",    [Parameter("self", None), Parameter("index", Number()), Parameter("value", None)], None),
            Function("length", [Parameter("self", None)], Number()),
        ])


class EqualityTrait(Trait):
    def __init__(self):
        super().__init__("Equality", [
            Function("eq", [Parameter("self", None), Parameter("other", None)], Boolean()),
            Function("ne", [Parameter("self", None), Parameter("other", None)], Boolean())
        ])


class OrdinalTrait(Trait):
    def __init__(self):
        super().__init__("Ordinal", [
            Function("lt", [Parameter("self", None), Parameter("other", None)], Boolean()),
            Function("le", [Parameter("self", None), Parameter("other", None)], Boolean()),
            Function("gt", [Parameter("self", None), Parameter("other", None)], Boolean()),
            Function("ge", [Parameter("self", None), Parameter("other", None)], Boolean())
        ])


class BooleanOpsTrait(Trait):
    def __init__(self):
        super().__init__("BooleanOps", [
            Function("and", [Parameter("self", None), Parameter("other", None)], Boolean()),
            Function("or",  [Parameter("self", None), Parameter("other", None)], Boolean()),
            Function("not", [Parameter("self", None)], Boolean())
        ])


class ArithmeticOpsTrait(Trait):
    def __init__(self):
        super().__init__("ArithmeticOps", [
            Function("plus",     [Parameter("self", None), Parameter("other", None)], None),
            Function("minus",    [Parameter("self", None), Parameter("other", None)], None),
            Function("multiply", [Parameter("self", None), Parameter("other", None)], None),
            Function("divide",   [Parameter("self", None), Parameter("other", None)], None),
            Function("modulo",   [Parameter("self", None), Parameter("other", None)], None),
            Function("pow",      [Parameter("self", None), Parameter("other", None)], None)
        ])


class NumberRepresentableTrait(Trait):
    def __init__(self):
        super().__init__("NumberRepresentable", [
            Function("to_number", [Parameter("self", None)], Number())
        ])

# =================================================================================================
# Expressions as defined in Section 3.4 of the IR specification:

class Expression(ABC):
    @abstractmethod
    def result_type(self, containing_type: Optional["ProtocolType"]) -> "ProtocolType":
        raise ProtocolTypeError("Expression MUST be subclassed")


@dataclass(frozen=True)
class ArgumentExpression(Expression):
    arg_name: str
    arg_value: Expression

    def result_type(self, containing_type: Optional["ProtocolType"]) -> "ProtocolType":
        return self.arg_value.result_type(containing_type)


@dataclass(frozen=True)
class MethodInvocationExpression(Expression):
    target      : Expression
    method_name : str
    arg_exprs   : List[ArgumentExpression]

    def __post_init__(self):
        if re.search(FUNC_NAME_REGEX, self.method_name) == None:
            raise ProtocolTypeError("Method {}: invalid name".format(self.method_name))

    def result_type(self, containing_type: Optional["ProtocolType"]) -> "ProtocolType":
        args   = [Argument(arg.arg_name, arg.result_type(containing_type), arg.arg_value) for arg in self.arg_exprs]
        result = self.target.result_type(containing_type)
        if result is None:
            raise ProtocolTypeError("Method {}: invalid arguments".format(self.method_name))
        method = result.get_method(self.method_name)
        if not method.is_method_accepting(result, args):
            raise ProtocolTypeError("Method {}: invalid arguments".format(self.method_name))
        return method.get_return_type()


@dataclass(frozen=True)
class FunctionInvocationExpression(Expression):
    func       : "Function"
    args_exprs : List[ArgumentExpression]

    def result_type(self, containing_type: Optional["ProtocolType"]) -> "ProtocolType":
        return self.func.get_return_type()


@dataclass(frozen=True)
class FieldAccessExpression(Expression):
    """
    An expression representing access to `field` of `target`.
    The `target` must be a structure type.
    """
    target     : Expression
    field_name : str

    def result_type(self, containing_type: Optional["ProtocolType"]) -> "ProtocolType":
        if isinstance(self.target.result_type(containing_type), Struct):
            struct = cast(Struct, self.target.result_type(containing_type))
            return struct.field(self.field_name).field_type
        else:
            raise ProtocolTypeError("Cannot access fields in object of type {}".format(self.target.result_type(containing_type)))


@dataclass(frozen=True)
class ContextAccessExpression(Expression):
    context    : "Context"
    field_name : str

    def result_type(self, containing_type: Optional["ProtocolType"]) -> "ProtocolType":
        return self.context.field(self.field_name).field_type


@dataclass(frozen=True)
class IfElseExpression(Expression):
    condition : Expression
    if_true   : Expression
    if_false  : Expression

    def result_type(self, containing_type: Optional["ProtocolType"]) -> "ProtocolType":
        result_type = self.condition.result_type(containing_type)
        if result_type != Boolean():
            raise ProtocolTypeError("Cannot create IfElseExpression: condition is not boolean")
        if self.if_true.result_type(containing_type) != self.if_false.result_type(containing_type):
            raise ProtocolTypeError("Cannot create IfElseExpression: branch types differ")
        return self.if_true.result_type(containing_type)


@dataclass(frozen=True)
class SelfExpression(Expression):
    def result_type(self, containing_type: Optional["ProtocolType"]) -> "ProtocolType":
        if containing_type is None:
            raise ProtocolTypeError("Cannot evaluate Self expression result type without a containing type")
        return containing_type


@dataclass(frozen=True)
class ConstantExpression(Expression):
    constant_type  : "ProtocolType"
    constant_value : Any

    def result_type(self, containing_type: Optional["ProtocolType"]) -> "ProtocolType":
        return self.constant_type


# =================================================================================================
# Protocol Types:

# -------------------------------------------------------------------------------------------------
# ProtocolType base class:

class ProtocolType:
    traits  : List["Trait"]
    methods : Dict[str, "Function"]
    parent  : Optional["ProtocolType"]

    def __init__(self, parent: Optional["ProtocolType"] = None):
        self.traits = []
        self.methods = {}
        self.parent = parent

    def implement_trait(self, trait: "Trait") -> None:
        if trait in self.traits:
            raise ProtocolTypeError(f"Type {self} already implements trait {trait.name}")
        else:
            self.traits.append(trait)
            for method in trait.methods:
                if method.name in self.methods:
                    raise ProtocolTypeError(f"Type {self} already implements a method {method.name}")
                else:
                    mimpl_name = method.name
                    mimpl_rt   = method.return_type if method.return_type is not None else self
                    mimpl_parameters = [Parameter(p.param_name, p.param_type if p.param_type is not None else self) for p in method.parameters]
                    self.methods[method.name] = Function(mimpl_name, mimpl_parameters, mimpl_rt)

    def get_method(self, method_name: str) -> "Function":
        method = None
        current_type = self
        while method is None:
            method = current_type.methods.get(method_name, None)
            if current_type.parent is not None:
                current_type = current_type.parent
            else:
                break
        if method is None:
            raise ProtocolTypeError(f"{self} and its parents do not implement the {method_name} method")
        return method

    def is_a(self, obj):
        parents = []
        while self.parent is not None:
            parents.append(self.parent)
            self = self.parent
        return obj in parents


# -------------------------------------------------------------------------------------------------
# ProtocolType mixins:

class PrimitiveType(ProtocolType, metaclass=Singleton):
    """
    PrimitiveTypes are instantiated only once, and cannot be constructed by a Protocol definition.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __post_init__(self):
        pass


class ConstructableType(ProtocolType):
    """
    ConstructableTypes are classes that are instantiated as constructors for ProtocolTypes.
    """
    name: str
    
    def __init__(self, name: Optional[str], **kwargs):
        super().__init__(**kwargs)
        if name is None:
            raise ProtocolTypeError(f"Cannot create type: types must be named")
        self.name = name

    def _validate_typename(self):
        if re.search(TYPE_NAME_REGEX, self.name) is None:
            raise ProtocolTypeError(f"Cannot create type {self.name}: malformed name")


class InternalType(ProtocolType):
    """
    InternalTypes are types that are needed to define a Protocol, but that do not represent data sent/received by a Protocol.
    """
    pass


class RepresentableType(ProtocolType):
    """
    RepresentableTypes are types that model data that can be sent/received by a Protocol.
    """
    size : Optional[Expression]
    
    def __init__(self, size: Optional[Expression] = None, **kwargs):
        super().__init__(**kwargs)
        self.size = size
        self.implement_trait(SizedTrait())


# -------------------------------------------------------------------------------------------------
# Representable, primitive types:

class Nothing(RepresentableType, PrimitiveType):
    def __init__(self):
        super().__init__(size=ConstantExpression(Number(), 0))


# -------------------------------------------------------------------------------------------------
# Representable, constructable types:

class BitString(RepresentableType, ConstructableType):
    def __init__(self, name: str, size: Optional[Expression]):
        super().__init__(name=name, size=size)
        self.implement_trait(ValueTrait())
        self.implement_trait(EqualityTrait())
        self.implement_trait(NumberRepresentableTrait())


class Option(RepresentableType, ConstructableType):
    reference_type : RepresentableType

    def __init__(self, name: str, reference_type: RepresentableType) -> None:
        super().__init__(name=name, size=reference_type.size)
        self.reference_type = reference_type


class Array(RepresentableType, ConstructableType):
    element_type : RepresentableType
    length       : Optional[Expression]
    
    def __init__(self, name: str, element_type: RepresentableType, length: Optional[Expression]):
        super().__init__(name=name, size=None)
        self.element_type = element_type
        self.length = length
        self.implement_trait(EqualityTrait())
        self.implement_trait(IndexCollectionTrait())


@dataclass(frozen=True)
class StructField():
    field_name: str
    field_type: "RepresentableType"
    is_present: Optional[Expression]


class Struct(RepresentableType, ConstructableType):
    fields      : Dict[str, StructField]
    constraints : List[Expression]
    actions     : List[Expression]
    
    def __init__(self, name: str) -> None:
        super().__init__(name=name)
        self.fields = {}
        self.constraints = []
        self.actions = []
        self.implement_trait(EqualityTrait())
    
    def add_field(self, field: StructField) -> None:
        if field.field_name in self.fields:
            raise ProtocolTypeError(f"{self.name} already contains a field named {field.field_name}")
        if re.search(FUNC_NAME_REGEX, field.field_name) is None:
            raise ProtocolTypeError(f"Cannot parse field {field.field_name}: malformed name")
        self.fields[field.field_name] = field
    
    def add_constraint(self, constraint: Expression) -> None:
        if constraint.result_type(self) != Boolean():
            raise ProtocolTypeError(f"Invalid constraint: {constraint.result_type(self)} != Boolean")
        self.constraints.append(constraint)
    
    def add_action(self, action: Expression) -> None:
        if action.result_type(self) != Nothing():
            raise ProtocolTypeError(f"Invalid action: {action.result_type(self)} != Nothing")
        self.actions.append(action)
        
    def field(self, field_name: str) -> StructField:
        if field_name not in self.fields:
            raise ProtocolTypeError(f"{self.name} has no field named {field_name}")
        return self.fields[field_name]

    def get_fields(self) -> List[StructField]:
        return list(self.fields.values())


class Enum(RepresentableType, ConstructableType):
    variants : List[RepresentableType]
    
    def __init__(self, name: str, variants: List[RepresentableType]) -> None:
        super().__init__(name=name, size=None)
        self.variants = variants


# -------------------------------------------------------------------------------------------------
# Internal, primitive types:

class Boolean(InternalType, PrimitiveType):
    def __post_init__(self):
        self.implement_trait(ValueTrait())
        self.implement_trait(EqualityTrait())
        self.implement_trait(BooleanOpsTrait())


class Number(InternalType, PrimitiveType):
    def __post_init__(self):
        self.implement_trait(ValueTrait())
        self.implement_trait(EqualityTrait())
        self.implement_trait(OrdinalTrait())
        self.implement_trait(ArithmeticOpsTrait())


# -------------------------------------------------------------------------------------------------
# Internal, constructable types:

@dataclass(frozen=True)
class Parameter:
    param_name : str
    param_type : Optional["ProtocolType"]


@dataclass(frozen=True)
class Argument:
    arg_name  : str
    arg_type  : Optional["ProtocolType"]
    arg_value : Any


class Function(InternalType, ConstructableType):
    parameters: List[Parameter]
    return_type: Optional[ProtocolType]
    
    def __init__(self, name: str, parameters: List[Parameter], return_type : Optional[ProtocolType]):
        super().__init__(name=name)
        self.parameters = parameters
        self.return_type = return_type
    
    def _validate_typename(self):
        if re.search(FUNC_NAME_REGEX, self.name) is None:
            raise ProtocolTypeError(f"Cannot create type {self.name}: malformed name")

    def is_method(self, self_type: "ProtocolType") -> bool:
        if self.parameters[0].param_name != "self":
            return False
        if self.parameters[0].param_type != self_type:
            return False
        return True

    def is_method_accepting(self, self_type: "ProtocolType", arguments: List[Argument]) -> bool:
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
            if (ptype != a.arg_type) and a.arg_type is not None and not a.arg_type.is_a(ptype):
                return False
        return True
    
    def get_return_type(self) -> ProtocolType:
        if self.return_type is None:
            return Nothing()
        else:
            return self.return_type


@dataclass(frozen=True)
class ContextField():
    field_name : str
    field_type : ProtocolType


class Context(InternalType, ConstructableType):
    fields: Dict[str, ContextField]

    def __init__(self, name: str):
        super().__init__(name=name)
        self.fields = {}

    def add_field(self, field: ContextField) -> None:
        if field.field_name in self.fields:
            raise ProtocolTypeError(f"{self.name} already has a field named {field.field_name}")
        self.fields[field.field_name] = field

    def field(self, field_name: str) -> ContextField:
        if field_name not in self.fields:
            raise ProtocolTypeError(f"{self.name} has no field named {field_name}")
        return self.fields[field_name]


class Protocol(InternalType, ConstructableType):
    _types   : Dict[str, ConstructableType]
    _funcs   : List[str]
    _context : Context
    _pdus    : List[str]
    
    def __init__(self):
        super().__init__(name="Protocol")
        self._types = {}
        self._funcs = []
        self._context = Context("Context")
        self._pdus = []
        self.define_bitstring("DataUnit", None)

    def _check_typename(self, name: str):
        if name in self._types:
            raise ProtocolTypeError(f"Cannot create type {self.name}: already exists")
        
    # =============================================================================================
    # Public API:
    
    def set_protocol_name(self, name: str) -> None:
        """
        Define the name of the protocol.
        
        Parameters:
        self - the protocol in which the new type is defined
        name - the name of the protocol
        """
        if self.name != "Protocol":
            raise ProtocolTypeError("Cannot redefine protocol name")
        self.name = name

    def define_bitstring(self, name: str, size: Optional[Expression]) -> BitString:
        """
        Define a new bit string type for this protocol.
        
        Parameters:
        self  - the protocol in which the new type is defined
        name  - the name of the new type
        size  - the size of the new type, in bits. None if variable
        """
        self._check_typename(name)
        newtype = BitString(name, size)
        self._types[name] = newtype
        return newtype

    def define_option(self, name: str, reference_type: RepresentableType) -> Option:
        """
        Define a new option type for this protocol.

        Parameters:
          self  - the protocol in which the new type is defined
          name  - the name of the new type
          reference_type - the type which this instantiation of Option will take (either Nothing or another representable type)
          size  - the size of reference_type (0 if Nothing, varies for other representable types)
        """
        self._check_typename(name)
        newtype = Option(name, reference_type)
        self._types[name] = newtype
        return newtype

    def define_array(self, name: str, element_type: RepresentableType, length: Optional[Expression]) -> Array:
        """
        Define a new array type for this protocol.

        Parameters:
          self  - the protocol in which the new type is defined
          name  - the name of the new type
          element_type - a Type object, representing the element type
          length - the number of elements in the array
        """
        self._check_typename(name)
        newtype = Array(name, element_type, length)
        self._types[name] = newtype
        return newtype

    def define_struct(self, name: str, fields: List[StructField], constraints: List[Expression], actions: List[Expression]) -> Struct:
        """
        Define a new structure type for this protocol.

        Parameters:
          self        - the protocol in which the new type is defined
          name        - the name of the new type
          fields      - the fields that are in the struct
          constraints - the constraints to define in the struct
          actions     - the action to define in the struct
        """
        self._check_typename(name)
        newtype = Struct(name)
        self._types[name] = newtype
        for field in fields:
            newtype.add_field(field)
        for constraint in constraints:
            newtype.add_constraint(constraint)
        for action in actions:
            newtype.add_action(action)
        return newtype

    def define_enum(self, name: str, variants: List[RepresentableType]) -> Enum:
        """
        Define a new enumerated type for this protocol.

        Parameters:
          self     - the protocol in which the new type is defined
          name     - the name of the new type
          variants - the variant types of the enum
        """
        self._check_typename(name)
        newtype = Enum(name, variants)
        self._types[name] = newtype
        return newtype

    def derive_type(self, name: str, derived_from: ConstructableType, also_implements: List[Trait]) -> ProtocolType:
        """
        Define a new derived type for this protocol.
        The type constructor is described in Section 3.3.5 of the IR specification.

        Parameters:
          self            - the protocol in which the new type is defined
          name            - the name of the new type
          derived_from    - the type that the new type is derived from
          also_implements - additional traits that are implemented
        """
        self._check_typename(name)
        self._types[name]         = copy(derived_from)
        self._types[name].name    = name
        self._types[name].methods = copy(derived_from.methods)
        for trait in also_implements:
            self._types[name].implement_trait(trait)
        return self._types[name]

    def define_function(self, name: str, parameters: List[Parameter], return_type: ProtocolType) -> Function:
        """
        Define a new function type for this protocol.

        Parameters:
          self        - the protocol in which the new type is defined
          name        - the name of the new function
          return_type - the type that the function returns
        """
        self._check_typename(name)
        newfunc = Function(name, parameters, return_type)
        self._types[name] = newfunc
        self._funcs.append(name)
        return newfunc

    def define_context_field(self, name: str, ptype: ProtocolType):
        """
        Define a context field for this protocol.

        Parameters:
          self   - the protocol whose context is to be added to
          name   - name of the field to be added
          ptype  - type of the field to be added
        """
        self._context.add_field(ContextField(name, ptype))

    def define_pdu(self, pdu: str) -> None:
        """
        Define a PDU for this protocol.

        Parameters:
          self  - the protocol in which the new type is defined
          pdu   - the name of a pre-existing type that is a PDU
        """
        assert pdu in self._types
        assert isinstance(self._types[pdu], RepresentableType)
        self._pdus.append(pdu)

    def get_protocol_name(self) -> Optional[str]:
        return self.name

    def has_type(self, type_name: str) -> bool:
        return type_name in self._types

    def get_type(self, type_name: str) -> ConstructableType:
        assert self.has_type(type_name)
        return self._types[type_name]

    def has_func(self, func_name: str) -> bool:
        return func_name in self._funcs

    def get_func(self, func_name: str) -> Function:
        assert isinstance(self._types[func_name], Function)
        return cast(Function, self._types[func_name])

    def get_context(self):
        return self._context

    def get_pdu(self, pdu_name: str) -> RepresentableType:
        return cast(RepresentableType, self._types[pdu_name])

    def get_pdu_names(self) -> List[str]:
        return self._pdus

    def get_type_names(self) -> List[str]:
        return list(self._types.keys())


# vim: set tw=0 ai:
