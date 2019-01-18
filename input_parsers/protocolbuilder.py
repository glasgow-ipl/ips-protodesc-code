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
from protocol import Protocol

#--------------------------------------------------------------------------------------------------
# Expressions
#--------------------------------------------------------------------------------------------------

class Expression:
    kind: str

    def __init__(self, kind: str):
        self.kind = kind

class ConstantExpression(Expression):
    type: str
    value: Any

    def __init__(self, type: str, value: Any):
        super().__init__("Constant")
        self.type = type
        self.value = value
        
    def json_repr(self):
        return {"expression" : self.kind,
                "type"       : self.type,
                "value"      : self.value}

#--------------------------------------------------------------------------------------------------
# Types
#--------------------------------------------------------------------------------------------------

class TypeConstructor:
    name: str
    
    def __init__(self, name):
        self.name = name
        
    def typecheck(self, defined_types: List[str]):
        pass
        
class BitStringConstructor(TypeConstructor):
    size: int
    
    def __init__(self, name=None, size=None):
        # if name is None, generate one
        if name is None:
            name = "BitString${}".format(size)

        super().__init__(name)
        self.size = size
        
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
        
    def typecheck(self, defined_types: List[str]):
        if self.element_type not in defined_types:
            raise Exception("{} has not been defined".format(self.element_type))

    def json_repr(self):
        return {"construct"    : "Array",
                "name"         : self.name,
                "element_type" : self.element_type,
                "length"       : self.length}
        
class StructField:
    field_name: str
    field_type: str
    is_present: Expression
    transform: Expression 
    
    def __init__(self, field_name: str, field_type: str, is_present: Expression, transform: Expression):
        self.field_name = field_name
        self.field_type = field_type
        self.is_present = is_present
        self.transform = transform
        
    def json_repr(self):
        return {"name"       : self.field_name,
                "type"       : self.field_type,
                "is_present" : self.is_present,
                "transform"  : self.transform}

class StructConstructor(TypeConstructor):
    fields: List[StructField]
    constraints: List[Expression]
    actions: List[Expression]
    
    def __init__(self, name, fields, constraints, actions):
        super().__init__(name)
        self.fields = fields
        self.constraints = constraints
        self.actions = actions

    def json_repr(self):
        return {"construct"   : "Struct",
                "name"        : self.name,
                "fields"      : self.fields,
                "constraints" : self.constraints,
                "actions"     : self.actions}

#--------------------------------------------------------------------------------------------------
# ProtocolBuilder
#--------------------------------------------------------------------------------------------------

class ProtocolBuilder:
    name: str
    definitions: Dict[str, TypeConstructor]
    pdus: List[str]

    def __init__(self, name=None):
        self.name = name
        self.definitions = {}
        self.pdus = []
        
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