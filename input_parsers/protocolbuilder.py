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
import json
import abc

from protocol import Protocol
from protocoltypes import *
from protocoltypeelements import *

#--------------------------------------------------------------------------------------------------
# Type Constructors
#--------------------------------------------------------------------------------------------------

class TypeConstructor(JSONRepresentable, abc.ABC):
    name: str
    types_used: List[str]
    
    def __init__(self, name):
        self.name = name
        self.types_used = []

    def typecheck(self, defined_types: List[str]):
        builtin_types = ["Nothing", "Boolean", "Size"]
        
        # check if name already defined
        if self.name in self.types_used or self.name in builtin_types:
            raise Exception("{} already defined".format(self.name))
            
        # check if any types used have not been defined
        for type_name in self.types_used:
            if type_name not in defined_types and type_name not in builtin_types:
                raise Exception("{} has not been defined".format(type_name))

    @abc.abstractmethod     
    def build_protocol_type(self) -> "Type":
        pass

class TraitConstructor(TypeConstructor):
    methods : Dict[str, Function]

    def __init__(self, name: str, methods: List[Function]) -> None:
        self.name    = name
        self.methods = {}
        for method in methods:
            self.methods[method.name] = method
    
    def build_protocol_type(self) -> Trait:
        return Trait(self.name, self.methods)

    def json_repr(self) -> Dict:
        return {"construct" : "Trait",
                "name"      : self.name,
                "methods"   : self.methods}
        
class BitStringConstructor(TypeConstructor):
    size: int
    
    def __init__(self, name=None, size=None):
        # if name is None, generate one
        if name is None:
            name = "BitString${}".format(size)

        super().__init__(name)
        self.size = size
    
    def build_protocol_type(self) -> BitString:
        return BitString(self.name, self.size)
        
    def json_repr(self):
        return {"construct" : "BitString",
                "name"      : self.name,
                "size"      : self.size}
        
class ArrayConstructor(TypeConstructor):
    element_type: str
    length: int
    
    def __init__(self, element_type, name=None, length=None):
        # if name is None, generate one
        if name is None:
            name = "{}${}".format(element_type, length)
            
        super().__init__(name)
        self.element_type = element_type
        self.length = length
        self.types_used.append(element_type)
    
    def build_protocol_type(self) -> Array:
        return Array(self.name, self.element_type, self.length)

    def json_repr(self):
        return {"construct"    : "Array",
                "name"         : self.name,
                "element_type" : self.element_type.name,
                "length"       : self.length}

class StructConstructor(TypeConstructor):
    fields: List[StructField]
    constraints: List[Expression]
    actions: List[Expression]
    
    def __init__(self, name, fields, constraints, actions):
        super().__init__(name)
        self.fields = fields
        self.constraints = constraints
        self.actions = actions
    
    def build_protocol_type(self) -> Struct:
        return Struct(self.name)

    def json_repr(self):
        return {"construct"   : "Struct",
                "name"        : self.name,
                "fields"      : self.fields,
                "constraints" : self.constraints,
                "actions"     : self.actions}

class EnumConstructor(TypeConstructor):
    variants: List["Type"]
    
    def __init__(self, name, variants):
        super().__init__(name)
        self.variants = variants
    
    def build_protocol_type(self) -> Enum:
        return Enum(self.name)
        
    def json_repr(self):
        return {"construct" : "Enum",
                "name"      : self.name,
                "variants"  : [{"type" : variant.name} for variant in variants]}

class NewTypeConstructor(TypeConstructor):
    derived_from: str
    implements: List[str]
    
    def __init__(self, name: str, derived_from: str, implements: List[str]):
        super().__init__(name)
        self.derived_from = derived_from
        self.implements = implements
        
        self.types_used.append(derived_from)
        
    def json_repr(self):
        return {"construct"    : "NewType",
                "name"         : self.name,
                "derived_from" : self.derived_from,
                "implements"   : [{"trait" : trait_name} for trait_name in self.implements]}

class FunctionConstructor(TypeConstructor):
    parameters: List[Parameter]
    return_type: str
    
    def __init__(self, name: str, parameters: List[Parameter], return_type: str):
        super().__init__(name)
        self.parameters = parameters
        self.return_type = return_type
        
    def build_protocol_type(self) -> Function:
        return Function(self.name)
        
    def json_repr(self):
        return {"construct"   : "Function",
                "name"        : self.name,
                "parameters"  : self.parameters,
                "return_type" : self.return_type}

#--------------------------------------------------------------------------------------------------
# ProtocolBuilder
#--------------------------------------------------------------------------------------------------

class ProtocolBuilder:
    name: str
    definitions: Dict[str, TypeConstructor]
    pdus: List[str]
    protocol: Protocol

    def __init__(self, name=None):
        self.name = name
        self.definitions = {}
        self.pdus = []
        self.protocol = Protocol()
        
    def set_protocol_name(self, name):
        self.name = name
        
    def add_definition(self, definition: TypeConstructor, warn_if_defined: bool = True):
        definition.typecheck(list(self.definitions.keys()))
        if warn_if_defined and definition.name in self.definitions:
            raise Exception("{} has already been defined".format(definition.name))
        else:
            self.definitions[definition.name] = definition
        
    def add_pdu(self, pdu_name: str):
        if pdu_name not in self.definitions:
            raise Exception("{} has not been defined".format(pdu_name))
        else:
            self.pdus.append(pdu_name)
    
    def json_repr(self):
        return {"construct"   : "Protocol",
                "name"        : self.name,
                "definitions" : list(self.definitions.values()),
                "pdus"        : [{"type" : pdu_name for pdu_name in self.pdus}]}
    
    def get_json_constructor(self):
        return json.dumps(self, default=lambda obj: obj.json_repr(), indent=4)

    def build_protocol(self) -> Protocol:
        protocol = Protocol()
        protocol.load(self.get_json_constructor())
        return protocol