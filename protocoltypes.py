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
from copy import deepcopy

from protocoltypeelements import *

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
# Traits:

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

    def implement_trait(self, trait: Trait):
        if trait in self.traits:
            raise TypeError("Type {} already implements trait {}".format(self.name, trait.name))
        else:
            # FIXME: how should we handle instantiation of unspecified types?
            # We could instantiate the here, replacing unspecified types with
            # self references. Alternatively, we could leave them unspecified,
            # and dynamically look-up the type when needed. The latter may be
            # better, once we start thinking about whether derived types are
            # proper subclasses...
            self.traits[trait.name] = trait
            for method_name in trait.methods:
                if method_name in self.methods:
                    raise TypeError("Type {} already implements method {}".format(self.name, method_name))
                else:
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
