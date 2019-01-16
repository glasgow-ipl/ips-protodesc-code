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

class Type:
    name: str

class BitString:
    name: str
    size: int

    def __init__(self, name=None, size=None):
        # if name is None, generate a name
        if name is None:
            name = "BitString$%s" % (str(size))
        
        self.name = name
        self.size = size
    
    def json_repr(self: 'BitString'):
        return {"construct" : "BitString",
                "name"      : self.name,
                "size"      : self.size}
                
class Array:
    name: str
    element_type: str
    length: int
    
    def __init__(self, element_type, name=None, length=None):
        # if name is None, generate a name
        if name is None:
            name = "%s$%s" % (element_type, str(length))
        
        self.name = name
        self.element_type = element_type
        self.length = length
    
    def json_repr(self):
        return {"construct"    : "Array",
                "name"         : self.name,
                "element_type" : self.element_type,
                "length"       : self.length}

class Transform:
    into_name: str
    into_type: str 
    using: str 
    
    def __init__(self, into_name, into_type, using):
        self.into_name = into_name
        self.into_type = into_type
        self.using = using
        
    def json_repr(self):
        return {"into_name" : self.into_name,
                "into_type" : self.into_type,
                "using"     : self.using}

class Expression:
    type: str
    
    def __init__(self, type):
        self.type = type

class Argument:
    name: str
    value: Expression
    
    def __init__(self, name, value):
        self.name = name
        self.value = value
        
    def json_repr(self):
        return {"name"  : self.name,
                "value" : self.value}

class MethodInvocation(Expression):
    target: Expression  
    method: str
    arguments: List[Argument]
    
    def __init__(self, target, method, arguments):
        super(MethodInvocation, self).__init__("MethodInvocation")
        self.target = target
        self.method = method
        self.arguments = arguments
        
    def json_repr(self):
        return {"expression" : self.type,
                "target"     : self.target,
                "method"     : self.method,
                "arguments"  : self.arguments}

class FunctionInvocation(Expression):
    name: str 
    arguments: List[Argument]
    
    def __init__(self, name, arguments):
        super(FunctionInvocation, self).__init__("FunctionInvocation")
        self.name = name
        self.arguments = arguments
        
    def json_repr(self):
        return {"expression" : self.type,
                "name"       : self.name,
                "arguments"  : self.arguments}

class FieldAccess(Expression):
    target: Expression
    field: str
    
    def __init__(self, target, field):
        super(FieldAccess, self).__init__("FieldAccess")
        self.target = target
        self.field = field
        
    def json_repr(self):
        return {"expression" : self.type,
                "target"     : self.target,
                "field"      : self.field}

class ContextAccess(Expression):
    field: str
    
    def __init__(self, field):
        super(ContextAccess, self).__init__("ContextAccess")
        self.field = field
        
    def json_repr(self):
        return {"expression" : self.type,
                "field"      : self.field}

class IfElse(Expression):
    condition: Expression
    if_true: Expression
    if_false: Expression
    
    def __init__(self, condition, if_true, if_false):
        super(IfElse, self).__init__("IfElse")
        self.condition = condition
        self.if_true = if_true
        self.if_false = if_false
    
    def json_repr(self):
        return {"expression" : self.type,
                "condition"  : self.condition,
                "if_true"    : self.if_true,
                "if_false"   : self.if_false}

class This(Expression):
    def __init__(self):
        super(This, self).__init__("This")
        
    def json_repr(self):
        return {"expression" : self.type}

class Constant(Expression):
    type_name: str 
    value: Any 
    
    def __init__(self):
        super(Constant, self).__init__("Constant")
        
    def json_repr(self):
        return {"expression" : self.type,
                "type"       : self.type_name,
                "value"      : self.value}

class Field:
    name: str
    type: str
    is_present: Expression
    transform: Transform
    
    def __init__(self, name, type, is_present, transform):
        self.name = name
        self.type = type
        self.is_present = is_present
        self.transform = transform
        
    def json_repr(self):
        return {"name"       : self.name,
                "type"       : self.type,
                "is_present" : self.is_present,
                "transform"  : self.transform}

class Structure:
    name: str
    fields: List[Field]
    constraints: List[Expression]
    actions: List[Expression]
    
    def __init__(self, name, fields, constraints, actions):
        self.name = name
        self.fields = fields
        self.constraints = constraints
        self.actions = actions
        
    def json_repr(self):
        return {"construct"   : "Struct",
                "name"        : self.name,
                "fields"      : self.fields,
                "constraints" : self.constraints,
                "actions"     : self.actions}
        