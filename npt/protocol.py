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
# Traits:

@dataclass(frozen=True)
class TypeVariable:
    name : str
    
    def __eq__(self, other: object) -> bool:
        return isinstance(other, TypeVariable) and self.name == other.name


@dataclass(frozen=True)
class Trait:
    name    : str
    methods : List["Function"]
        
    def __eq__(self, other: object) -> bool:
        return isinstance(other, Trait) and self.name == other.name and self.methods == other.methods


class Value(Trait):
    def __init__(self):
        super().__init__("Value", [
            Function("get", [Parameter("self", TypeVariable("T"))], TypeVariable("T")),
            Function("set", [Parameter("self", TypeVariable("T")), Parameter("value", TypeVariable("T"))], Nothing())
        ])


class Sized(Trait):
    def __init__(self):
        super().__init__("Sized", [
            Function("size", [Parameter("self", TypeVariable("T"))], Number())
        ])


class IndexCollection(Trait):
    def __init__(self):
        super().__init__("IndexCollection", [
            Function("get",    [Parameter("self", TypeVariable("T")), Parameter("index", Number())], TypeVariable("ET")),
            Function("set",    [Parameter("self", TypeVariable("T")), Parameter("index", Number()), Parameter("value", TypeVariable("ET"))], Nothing()),
            Function("length", [Parameter("self", TypeVariable("T"))], Number()),
        ])


class Equality(Trait):
    def __init__(self):
        super().__init__("Equality", [
            Function("eq", [Parameter("self", TypeVariable("T")), Parameter("other", TypeVariable("T"))], Boolean()),
            Function("ne", [Parameter("self", TypeVariable("T")), Parameter("other", TypeVariable("T"))], Boolean())
        ])


class Ordinal(Trait):
    def __init__(self):
        super().__init__("Ordinal", [
            Function("lt", [Parameter("self", TypeVariable("T")), Parameter("other", TypeVariable("T"))], Boolean()),
            Function("le", [Parameter("self", TypeVariable("T")), Parameter("other", TypeVariable("T"))], Boolean()),
            Function("gt", [Parameter("self", TypeVariable("T")), Parameter("other", TypeVariable("T"))], Boolean()),
            Function("ge", [Parameter("self", TypeVariable("T")), Parameter("other", TypeVariable("T"))], Boolean())
        ])


class BooleanOps(Trait):
    def __init__(self):
        super().__init__("BooleanOps", [
            Function("and", [Parameter("self", TypeVariable("T")), Parameter("other", TypeVariable("T"))], Boolean()),
            Function("or",  [Parameter("self", TypeVariable("T")), Parameter("other", TypeVariable("T"))], Boolean()),
            Function("not", [Parameter("self", TypeVariable("T"))], Boolean())
        ])


class ArithmeticOps(Trait):
    def __init__(self):
        super().__init__("ArithmeticOps", [
            Function("plus",     [Parameter("self", TypeVariable("T")), Parameter("other", TypeVariable("T"))], TypeVariable("T")),
            Function("minus",    [Parameter("self", TypeVariable("T")), Parameter("other", TypeVariable("T"))], TypeVariable("T")),
            Function("multiply", [Parameter("self", TypeVariable("T")), Parameter("other", TypeVariable("T"))], TypeVariable("T")),
            Function("divide",   [Parameter("self", TypeVariable("T")), Parameter("other", TypeVariable("T"))], TypeVariable("T")),
            Function("modulo",   [Parameter("self", TypeVariable("T")), Parameter("other", TypeVariable("T"))], TypeVariable("T")),
            Function("pow",      [Parameter("self", TypeVariable("T")), Parameter("other", TypeVariable("T"))], TypeVariable("T"))
        ])


class NumberRepresentable(Trait):
    def __init__(self):
        super().__init__("NumberRepresentable", [
            Function("to_number", [Parameter("self", TypeVariable("T"))], Number())
        ])

# =================================================================================================
# Expressions as defined in Section 3.4 of the IR specification:

class Expression(ABC):
    @abstractmethod
    def result_type(self, containing_type: Optional["ProtocolType"]) -> "ProtocolType":
        """ Expression is an abstract class whose sub-classes must implement result_type() """


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
        method = result.get_method(self.method_name)
        if not method.is_method_accepting(result, args):
            raise ProtocolTypeError(f"Method {self.method_name}: invalid arguments")
        rt = method.get_return_type()
        if isinstance(rt, TypeVariable):
            raise ProtocolTypeError(f"Method {self.method_name}: unresolved type variable as return type")
        return rt


@dataclass(frozen=True)
class FunctionInvocationExpression(Expression):
    func      : "Function"
    arg_exprs : List[ArgumentExpression]

    def result_type(self, containing_type: Optional["ProtocolType"]) -> "ProtocolType":
        if not self.func.accepts_arguments([Argument(arg.arg_name, arg.result_type(containing_type), arg.arg_value) for arg in self.arg_exprs]):
            raise ProtocolTypeError(f"Function {self.func.name}: invalid arguments")
        rt = self.func.get_return_type()
        if isinstance(rt, TypeVariable):
            raise ProtocolTypeError(f"Function {self.func.name}: unresolved type variable as return type")
        return rt


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
            raise ProtocolTypeError(f"Cannot access fields in object of type {self.target.result_type(containing_type)}")


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

    def implement_trait(self, trait: "Trait", type_variables: Dict[TypeVariable, "ProtocolType"] = {}) -> None:
        type_variables = {TypeVariable("T") : self, **type_variables}
        if trait in self.traits:
            raise ProtocolTypeError(f"Type {self} already implements trait {trait.name}")
        else:
            for method in trait.methods:
                if method.name in self.methods:
                    raise ProtocolTypeError(f"Type {self} already implements a method {method.name}")
                else:
                    mimpl_name = method.name
                    mimpl_rt   = method.return_type if not isinstance(method.return_type, TypeVariable) else type_variables[method.return_type]
                    mimpl_parameters = [Parameter(p.param_name, p.param_type if not isinstance(p.param_type, TypeVariable) else type_variables[p.param_type]) for p in method.parameters]
                    self.methods[method.name] = Function(mimpl_name, mimpl_parameters, mimpl_rt)
            self.traits.append(trait)        

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

    def __str__(self):
        return f"{type(self).__name__}<::{' '.join([trait.name for trait in self.traits])}>"


# -------------------------------------------------------------------------------------------------
# ProtocolType mixins:

class Singleton(type):
    _instances : Dict["Singleton", "Singleton"] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
            cls._instances[cls].__post_init__()
        return cls._instances[cls]

    def __post_init__(self):
        pass

class PrimitiveType(ProtocolType, metaclass=Singleton):
    """
    PrimitiveTypes are instantiated only once, and cannot be constructed by a Protocol definition.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __post_init__(self):
        pass

    def __eq__(self, obj: object) -> bool:
        return isinstance(obj, type(self))

    def implement_trait(self, trait: Trait, type_variables: Dict[TypeVariable, ProtocolType] = {}):
        raise ProtocolTypeError(f"Cannot implement trait {trait.name} on a primitive type")


class ConstructableType(ProtocolType):
    """
    ConstructableTypes are classes that are instantiated as constructors for ProtocolTypes.
    """
    name: str
    
    def __init__(self, name: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        if name is None:
            raise ProtocolTypeError(f"Cannot create type: types must be named")
        self.name = name
        self._validate_typename()

    def _validate_typename(self):
        if re.search(TYPE_NAME_REGEX, self.name) is None:
            raise ProtocolTypeError(f"Cannot create type {self.name}: malformed name")

    def __str__(self):
        return f"{type(self).__name__}<{self.name}::{' '.join([trait.name for trait in self.traits])}>"
    
    def derive_from(self, name: str, also_implements: List[Trait]) -> "ConstructableType":
        """
        Derive a new type from this type.
        
        Parameters:
            self            - the type that the new type is derived from
            name            - the name of the new type
            also_implements - additional traits that the new type implements
        """
        new_type = copy(self)
        new_type.name = name
        new_type.methods = copy(self.methods)
        for trait in also_implements:
            new_type.implement_trait(trait)
        return new_type


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
        ProtocolType.implement_trait(self, Sized())

# -------------------------------------------------------------------------------------------------
# Representable, primitive types:

class Nothing(RepresentableType, PrimitiveType):
    def __init__(self):
        super().__init__(size=ConstantExpression(Number(), 0))
    
    def __post_init__(self):
        pass

# -------------------------------------------------------------------------------------------------
# Representable, constructable types:

class BitString(RepresentableType, ConstructableType):
    def __init__(self, name: str, size: Optional[Expression]):
        super().__init__(name=name, size=size)
        self.implement_trait(Value())
        self.implement_trait(Equality())
        self.implement_trait(NumberRepresentable())


class Option(RepresentableType, ConstructableType):
    reference_type : RepresentableType

    def __init__(self, name: str, reference_type: RepresentableType) -> None:
        super().__init__(name=name, size=reference_type.size)
        self.reference_type = reference_type


class Array(RepresentableType, ConstructableType):
    element_type : RepresentableType
    length       : Optional[Expression]
    parse_from   : Optional["Function"]
    serialise_to : Optional["Function"]

    def __init__(self, name: str, element_type: RepresentableType, length: Optional[Expression]):
        super().__init__(name=name, size=None)
        self.element_type = element_type
        self.length = length
        self.parse_from = None
        self.serialise_to = None
        self.implement_trait(Equality())
        self.implement_trait(IndexCollection(), {TypeVariable("ET"): element_type})
        
        #if self.length is None and element_type.size is None:
        #    raise ProtocolTypeError(f"Cannot construct Array: one of length or element size must be specified")
        # FIXME: ^ need to ensure that other ProtocolType sizes are resolved before checking this
        if self.length is not None and element_type.size is not None:
            self.size = MethodInvocationExpression(element_type.size, "mul", [ArgumentExpression("other", self.length)])


class StructField():
    field_name: str
    field_type: "RepresentableType"
    is_present: Expression
    
    def __init__(self, field_name: str, field_type: "RepresentableType", is_present: Optional[Expression] = None):
        self.field_name = field_name
        if re.search(FUNC_NAME_REGEX, field_name) is None:
            raise ProtocolTypeError(f"Cannot create field {field_name}: malformed name")
        self.field_type = field_type
        if is_present is not None:
            self.is_present = is_present
        else:
            self.is_present = ConstantExpression(Boolean(), True)


class Struct(RepresentableType, ConstructableType):
    fields      : Dict[str, StructField]
    constraints : List[Expression]
    actions     : List[Expression]
    parse_from   : Optional["Function"]
    serialise_to : Optional["Function"]

    def __init__(self, name: str, fields: List[StructField], constraints: List[Expression], actions: List[Expression]) -> None:
        super().__init__(name=name)
        self.fields = {}
        self.constraints = []
        self.actions = []
        for field in fields:
            self.add_field(field)
        for constraint in constraints:
            self.add_constraint(constraint)
        for action in actions:
            self.add_action(action)
        self.parse_from = None
        self.serialise_to = None
        self.implement_trait(Equality())
    
    def add_field(self, field: StructField) -> None:
        if field.field_name in self.fields:
            raise ProtocolTypeError(f"{self.name} already contains a field named {field.field_name}")
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
    variants     : List[RepresentableType]
    parse_from   : Optional["Function"]
    serialise_to : Optional["Function"]

    def __init__(self, name: str, variants: List[RepresentableType]) -> None:
        super().__init__(name=name, size=None)
        self.variants = variants
        self.parse_from   = None
        self.serialise_to = None


# -------------------------------------------------------------------------------------------------
# Internal, primitive types:

class Boolean(PrimitiveType, InternalType):
    def __post_init__(self):
        ProtocolType.implement_trait(self, Value())
        ProtocolType.implement_trait(self, Equality())
        ProtocolType.implement_trait(self, BooleanOps())


class Number(PrimitiveType, InternalType):
    def __post_init__(self):
        ProtocolType.implement_trait(self, Value())
        ProtocolType.implement_trait(self, Equality())
        ProtocolType.implement_trait(self, Ordinal())
        ProtocolType.implement_trait(self, ArithmeticOps())

# -------------------------------------------------------------------------------------------------
# Internal, constructable types:

@dataclass(frozen=True)
class Parameter:
    param_name : str
    param_type : Union[ProtocolType, TypeVariable]


@dataclass(frozen=True)
class Argument:
    arg_name  : str
    arg_type  : Union[ProtocolType, TypeVariable]
    arg_value : Any


class Function(InternalType, ConstructableType):
    parameters  : List[Parameter]
    return_type : Union[ProtocolType, TypeVariable]
    
    def __init__(self, name: str, parameters: List[Parameter], return_type : Union[ProtocolType, TypeVariable]):
        super().__init__(name=name)
        self.parameters = parameters
        self.return_type = return_type
    
    def _validate_typename(self):
        if re.search(FUNC_NAME_REGEX, self.name) is None:
            raise ProtocolTypeError(f"Cannot create type {self.name}: malformed name")

    def is_method(self) -> bool:
        return self.parameters[0].param_name == "self"

    def accepts_arguments(self, arguments: List[Argument]) -> bool:
        """
        Check if this function accepts the specified arguments
        """
        for (p, a) in zip(self.parameters, arguments):
            if isinstance(p.param_type, TypeVariable):
                raise ProtocolTypeError(f"Cannot evaluate signature of Function {self.name}: unresolved type variables")
            if (p.param_name != a.arg_name):
                return False
            if (p.param_type != a.arg_type) and not isinstance(a.arg_type, TypeVariable) and not a.arg_type.is_a(p.param_type):
                return False
        return True
    
    def is_method_accepting(self, self_type: "ProtocolType", arguments: List[Argument]) -> bool:
        """
        Check if this function is a method and accepts the specified arguments when invoked on an
        object of type self_type
        """
        return self.is_method() and self.accepts_arguments([Argument("self", self_type, TypeVariable("T"))] + arguments)
        
    def get_return_type(self) -> Union[ProtocolType, TypeVariable]:
        return self.return_type
            
    def __eq__(self, obj: object) -> bool:
        return isinstance(obj, Function) and self.name == obj.name and self.parameters == obj.parameters and self.return_type == obj.return_type


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
        
    def get_fields(self) -> List[ContextField]:
        return list(self.fields.values())


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
        # data_size is a field in the context, to be set to the size of incoming PDUs
        self._context.add_field(ContextField("data_size", Number()))
        # DataUnit is the type that represents incoming PDUs, and is sized to data_size
        self.add_type(BitString("DataUnit", ContextAccessExpression(self._context, "data_size")))

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

    def add_type(self, new_type: ConstructableType) -> ConstructableType:
        """
        Add a new type to this protocol.
        
        Parameters:
            self  - the protocol to which the type is added
            new_type - the type to be added to the protocol
        """
        self._check_typename(new_type.name)
        self._types[new_type.name] = new_type
        return new_type

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

    def synthesise(self) -> None:
        for ptype in self._types.values():
            if isinstance(ptype, Struct) or isinstance(ptype, Array) or isinstance(ptype, Enum):
                if ptype.parse_from is None:
                    pf_func = Function(f"parse_to_{ptype.name.lower()}",
                                        [Parameter("from", self.get_type("DataUnit"))],
                                        Option("PTReturn", ptype))
                    ptype.parse_from = pf_func
                if ptype.serialise_to is None:
                    st_func = Function(f"serialise_from_{ptype.name.lower()}",
                                        [Parameter("from", ptype)],
                                        Option("STReturn", cast(RepresentableType, self.get_type("DataUnit"))))
                    ptype.serialise_to = st_func

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
