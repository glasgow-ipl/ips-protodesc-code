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

import json
import re

# Type names begin with an upper case letter, function names do not:
TYPE_NAME_REGEX = "^[A-Z][A-Za-z0-9$_]+$"
FUNC_NAME_REGEX = "^[a-z][A-Za-z0-9$_]+$"

class IRError(Exception):
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
    def __init__(self, name, methods):
        self.name    = name
        self.methods = methods

    def __str__(self):
        print("Trait<{}>".format(self.name))

# =================================================================================================
# Expressions:

class Expression:
    pass

class MethodInvocationExpression:
    def __init__(self, target, method, args):
        if re.search(FUNC_NAME_REGEX, method) == None:
            raise IRError("Cannot create expression {}: malformed method name".format(method))
        self.kind   = "MethodInvocation"
        self.target = target
        self.method = method
        self.args   = args

    def type(self):
        target = self.target.type()
        method = target.get_method(self.method)
        return method.return_type

class FunctionInvocationExpression:
    def __init__(self, name, args):
        if re.search(FUNC_NAME_REGEX, name) == None:
            raise IRError("Cannot create expression {}: malformed function name".format(name))
        self.kind   = "FunctionInvocation"
        self.name   = method
        self.args   = args

    def type(self):
        # FIXME: implement this
        raise IRError("unimplemented (FunctionInvocationExpression::type)")

class FieldAccessExpression:
    def __init__(self, target, field):
        if target.type().kind != "Struct":
            raise IRError("Cannot access field of object with type {}".format(target.type()))
        self.target = target
        self.field  = field

    def type(self):
        target = self.target.type()
        field  = target.get_field(self.field)
        return field.type

class ContextAccessExpression:
    def __init__(self, field):
        self.field = field

    def type(self):
        # FIXME: implement this
        raise IRError("unimplemented (ContextAccessExpression::type)")

class IfElseExpression:
    def __init__(self, condition, if_true, if_false):
        self.condition = condition
        self.if_true   = if_true
        self.if_false  = if_false
        if if_true.type() != if_false.type():
            raise IRError("Cannot create expression: IfElse branch types differ")
        if condition.type() != self.get_type["Boolean"]:
            raise IRError("Cannot create expression: IfElse condition not Boolean")

    def type(self):
        return self.if_true.type()

class ThisExpression:
    def __init__(self, this):
        self.this = this

    def type(self):
        return self.this

class ConstantExpression:
    def __init__(self, type_, value):
        self.type_ = type_
        self.value = value

    def type(self):
        return self.type_

# =================================================================================================
# Fields in a structure or the context:

class Field:
    def __init__(self, name_, type_, is_present_, transform_):
        self.name       = name_
        self.type       = type_
        self.is_present = is_present_
        self.transform  = transform_

    def __str__(self):
        return "Field<{},{},{},{}>".format(self.name, self.type, self.is_present, self.transform)

class Transform:
    def __init__(self, into_name, into_type, using):
        self.into_name = into_name
        self.into_type = into_type
        self.using     = using

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

    def implement_trait(self, trait):
        if trait in self.traits:
            raise IRError("Cannot implement trait {} for type {}: already implemented".format(trait.name, self.name))
        else:
            self.traits[trait.name] = trait
            for method in trait.methods:
                if method.name in self.methods:
                    raise IRError("Cannot add method {} for type {}: already implemented".format(method.name, self.name))
                else:
                    self.methods[method.name] = method

    def get_method(self, method_name):
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

    def add_field(self, field):
        self.fields.append(field)

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    def add_action(self, action):
        self.actions.append(action)

    def get_field(self, field_name):
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

class Protocol:
    def __init__(self):
        # Define the primitive types:
        self._types = {}
        self._types["Nothing"] = Nothing()
        self._types["Boolean"] = Boolean()
        self._types["Size"]    = Size()
        # Define the standard traits:
        self._traits = {}
        self._traits["Value"] = Trait("Value", [
                                    Function("get", [Parameter("self", None)                                                                    ], None),
                                    Function("set", [Parameter("self", None), Parameter("value", None)                                          ], None)
                                ])
        self._traits["Sized"] = Trait("Sized", [
                                    Function("size",   [Parameter("self", None)                                                                 ], self.type("Size"))
                                ])
        self._traits["IndexCollection"] = Trait("IndexCollection", [
                                    Function("get",    [Parameter("self", None), Parameter("index", self.type("Size"))                          ], None),
                                    Function("set",    [Parameter("self", None), Parameter("index", self.type("Size")), Parameter("value", None)], None),
                                    Function("length", [Parameter("self", None)                                                                 ], self.type("Size"))
                                ])
        self._traits["Equality"] = Trait("Equality", [
                                    Function("eq",     [Parameter("self", None), Parameter("other", None)                                       ], self.type("Boolean")),
                                    Function("ne",     [Parameter("self", None), Parameter("other", None)                                       ], self.type("Boolean"))
                                ])
        self._traits["Ordinal"] = Trait("Ordinal", [
                                    Function("lt",     [Parameter("self", None), Parameter("other", None)                                       ], self.type("Boolean")),
                                    Function("le",     [Parameter("self", None), Parameter("other", None)                                       ], self.type("Boolean")),
                                    Function("gt",     [Parameter("self", None), Parameter("other", None)                                       ], self.type("Boolean")),
                                    Function("ge",     [Parameter("self", None), Parameter("other", None)                                       ], self.type("Boolean"))
                                ])
        self._traits["BooleanOps"] = Trait("BooleanOps", [
                                    Function("and",    [Parameter("self", None), Parameter("other", None)                                       ], self.type("Boolean")),
                                    Function("or",     [Parameter("self", None), Parameter("other", None)                                       ], self.type("Boolean")),
                                    Function("not",    [Parameter("self", None)                                                                 ], self.type("Boolean"))
                                ])
        self._traits["ArithmeticOps"] = Trait("ArithmeticOps", [
                                    Function("plus",    [Parameter("self", None), Parameter("other", None)                                      ], None),
                                    Function("minus",   [Parameter("self", None), Parameter("other", None)                                      ], None),
                                    Function("multiply",[Parameter("self", None)                                                                ], None),
                                    Function("divide",  [Parameter("self", None)                                                                ], None),
                                    Function("modulo",  [Parameter("self", None)                                                                ], None)
                                ])
        # Implement standard traits:
        self.type("Boolean").implement_trait(self.trait("Value"))
        self.type("Boolean").implement_trait(self.trait("Equality"))
        self.type("Boolean").implement_trait(self.trait("BooleanOps"))
        self.type("Size").implement_trait(self.trait("Value"))
        self.type("Size").implement_trait(self.trait("Equality"))
        self.type("Size").implement_trait(self.trait("Ordinal"))
        self.type("Size").implement_trait(self.trait("ArithmeticOps"))
        # Functions:
        self._funcs = {}

    # =============================================================================================
    # Private helper functions:

    def _validate_irtype(self, irobj, kind):
        if irobj["construct"] != kind:
            raise IRError("Cannot create {} from {} object".format(kind, irobj["construct"]))
        if irobj["name"] in self._types:
            raise IRError("Cannot create type {}: already exists".format(irobj["name"]))
        if re.search(TYPE_NAME_REGEX, irobj["name"]) == None:
            raise IRError("Cannot create type {}: malformed name".format(irobj["name"]))

    def _parse_arguments(self, args, this):
        res = []
        for arg in args:
            name_  = arg["name"]
            expr_  = self._parse_expression(arg["value"], this)
            type_  = expr_.type()
            # FIXME: what is the value?
            value_ = None
            res.append(Argument(name_, type_, value_))
        return res

    def _parse_expression(self, expr, this):
        if   expr["expression"] == "MethodInvocation":
            target = self._parse_expression(expr["target"], this)
            method = expr["method"]
            args   = self._parse_arguments(expr["arguments"], this)
            return MethodInvocationExpression(target, method, args)
        elif expr["expression"] == "FunctionInvocation":
            name   = self._funcs(expr["name"])
            args   = self._parse_arguments(expr["arguments"])
            return FunctionInvocationExpression(target, methods, args)
        elif expr["expression"] == "FieldAccess":
            target = self._parse_expression(expr["target"], this)
            field  = expr["field"]
            return FieldAccessExpression(target, field)
        elif expr["expression"] == "ContextAccess":
            field  = expr["field"]
            return ContextAccessExpression(target, field)
        elif expr["expression"] == "IfElse":
            condition = self._parse_expression(expr["condition"], this)
            if_true   = self._parse_expression(expr["if_true"],   this)
            if_false  = self._parse_expression(expr["if_false"],  this)
            return IfElseExpression(condition, if_true, if_false)
        elif expr["expression"] == "This":
            return ThisExpression(this)
        elif expr["expression"] == "Constant":
            type_ = self.type(expr["type"])
            value = expr["value"]
            return ConstantExpression(type_, value)
        else:
            raise IRError("Cannot parse expression: {}".format(expr["expression"]))
        
    def _parse_transform(self, transform):
        if transform != None:
            into_name = transform["into_name"]
            into_type = self.type(transform["into_type"])
            using     = self.func(transform["using"])
        else:
            None

    def _parse_fields(self, fields, this):
        res = []
        for field in fields:
            if re.search(FUNC_NAME_REGEX, field["name"]) == None:
                raise IRError("Cannot parse field {}: malformed name".format(field["name"]))
            _name       = field["name"]
            _type       = self.type(field["type"])
            _is_present = self._parse_expression(field["is_present"], this)
            _transform  = self._parse_transform(field["transform"])
            res.append(Field(_name, _type, _is_present, _transform))
        return res

    def _parse_constraints(self, constraints, this):
        res = []
        for constraint in constraints:
            expr = self._parse_expression(constraint, this)
            if expr.type() != self.type("Boolean"):
                raise IRError("Cannot parse constraint: {} != Boolean".format(expr.type()))
            res.append(expr)
        return res

    def _parse_actions(self, expression, this):
        # FIXME: implement this
        raise IRError("unimplemented (_parse_actions)")

    def _parse_variants(self, expression):
        # FIXME: implement this
        raise IRError("unimplemented (_parse_variants)")

    def _parse_parameters(self, parameters):
        res = []
        for p in parameters:
            res.append(Parameter(p["name"], self.type(p["type"])))
        return res

    # =============================================================================================
    # Public API:

    def add_bitstring(self, irobj):
        self._validate_irtype(irobj, "BitString")
        name         = irobj["name"]
        size         = irobj["size"]
        self._types[name] = BitString(name, size)
        self._types[name].implement_trait(self.trait("Sized"))
        self._types[name].implement_trait(self.trait("Value"))
        self._types[name].implement_trait(self.trait("Equality"))

    def add_array(self, irobj):
        self._validate_irtype(irobj, "Array")
        name         = irobj["name"]
        element_type = self._types[irobj["element_type"]]
        length       = irobj["length"]
        self._types[name] = Array(name, element_type, length)
        self._types[name].implement_trait(self.trait("Sized"))
        self._types[name].implement_trait(self.trait("Equality"))
        self._types[name].implement_trait(self.trait("IndexCollection"))

    def add_struct(self, irobj):
        self._validate_irtype(irobj, "Struct")
        name         = irobj["name"]
        self._types[name] = Struct(irobj["name"])
        for field in self._parse_fields(irobj["fields"], self._types[name]):
            self._types[name].add_field(field)
        for constraint in self._parse_constraints(irobj["constraints"], self._types[name]):
            self._types[name].add_constraint(constraint)
        for action in self._parse_actions(irobj["actions"], self._types[name]):
            self._types[name].add_action(action)
        self._types[name].implement_trait(self.trait("Sized"))

    def add_enum(self, irobj):
        self._validate_irtype(irobj, "Enum")
        name         = irobj["name"]
        variants     = self._parse_variants(irobj["variants"])
        self._types[name] = Enum(name, variants)
        self._types[name].implement_trait(self.trait("Sized"))

    def add_newtype(self, irobj):
        self._validate_irtype(irobj, "NewType")
        # FIXME: implement this
        raise IRError("unimplemented (add_newtype)")
        # FIXME: add trait implementations

    def add_function(self, irobj):
        if irobj["construct"] != "Function":
            raise IRError("Cannot create Function from {} object".format(irobj["construct"]))
        if irobj["name"] in self._funcs:
            raise IRError("Cannot create Function {}: already exists".format(irobj["name"]))
        if re.search(FUNC_NAME_REGEX, irobj["name"]) == None:
            raise IRError("Cannot create Function {}: malformed name".format(irobj["name"]))

        name        = irobj["name"]
        params      = self._parse_parameters(irobj["parameters"])
        return_type = self.type(irobj["return_type"])
        self._funcs[name] = Function(name, params, return_type)

    def type(self, name):
        return self._types[name]

    def func(self, name):
        return self._funcs[name]

    def trait(self, name):
        return self._traits[name]

    def typecheck(self):
        # FIXME: implement this
        raise IRError("unimplemented (typecheck)")

# =================================================================================================
# Unit tests:

import unittest

class TestProtocol(unittest.TestCase):
    def test_add_bitstring(self):
        protocol = Protocol()
        protocol.add_bitstring({
            "construct"    : "BitString",
            "name"         : "Timestamp",
            "size"         : 32
        })
        res = protocol.type("Timestamp")
        self.assertEqual(res.kind, "BitString")
        self.assertEqual(res.name, "Timestamp")
        self.assertEqual(res.size, 32)

    def test_add_array(self):
        protocol = Protocol()
        protocol.add_bitstring({
            "construct"    : "BitString",
            "name"         : "SSRC",
            "size"         : 32
        })
        protocol.add_array({
            "construct"    : "Array",
            "name"         : "CSRCList",
            "element_type" : "SSRC",
            "length"       : 4
        })
        res = protocol.type("CSRCList")
        self.assertEqual(res.kind, "Array")
        self.assertEqual(res.name, "CSRCList")
        self.assertEqual(res.element_type, protocol.type("SSRC"))
        self.assertEqual(res.length, 4)
        self.assertEqual(res.size, 128)

    def test_add_struct(self):
        protocol = Protocol()
        protocol.add_bitstring({
            "construct" : "BitString",
            "name"      : "SeqNumTrans",
            "size"      : 16
        })
        protocol.add_bitstring({
            "construct" : "BitString",
            "name"      : "SeqNum",
            "size"      : 16
        })
        protocol.add_bitstring({
            "construct" : "BitString",
            "name"      : "Timestamp",
            "size"      : 32
        })
        protocol.add_function({
            "construct"   : "Function",
            "name"        : "transform_seq",
            "parameters"  : [
            {
                "name" : "seq",
                "type" : "SeqNum"
            }],
            "return_type" : "SeqNumTrans"
        })
        protocol.add_struct({
            "construct"   : "Struct",
            "name"        : "TestStruct",
            "fields"      : [
                {
                    "name"       : "seq",
                    "type"       : "SeqNum",
                    "is_present" : {
                        "expression" : "Constant",
                        "type"       : "Boolean",
                        "value"      : "True"
                    },
                    "transform"  : {
                        "into_name" : "ext_seq",
                        "into_type" : "SeqNumTrans",
                        "using"     : "transform_seq"
                    }
                },
                {
                    "name"       : "ts",
                    "type"       : "Timestamp",
                    "is_present" : {
                        "expression" : "Constant",
                        "type"       : "Boolean",
                        "value"      : "True"
                    },
                    "transform"  : None
                }
            ],
            "constraints" : [
                {
                    "expression" : "MethodInvocation",
                    "target"     : {
                        "expression" : "FieldAccess",
                        "target"     : {
                            "expression" : "This"
                        },
                        "field"     : "seq"
                    },
                    "method"     : "eq",
                    "arguments"  : [
                        {
                            "name"  : "other",
                            "value" : {
                                "expression" : "Constant",
                                "type"       : "SeqNum",
                                "value"      : 47
                            }
                        }
                    ]
                }
            ],
            "actions" : [
            ]
        })
        res = protocol.type("TestStruct")
        self.assertEqual(res.kind, "Struct")
        self.assertEqual(res.name, "TestStruct")
        self.assertEqual(res.fields[0].name, "seq")
        self.assertEqual(res.fields[0].type, protocol.type("SeqNum"))
        # FIXME: add test for fields[0].is_present
        # FIXME: add test for fields[0].transform
        self.assertEqual(res.fields[1].name, "ts")
        self.assertEqual(res.fields[1].type, protocol.type("Timestamp"))
        # FIXME: add test for fields[1].is_present
        # FIXME: add test for fields[1].transform
        # FIXME: add test for constraints
        # FIXME: add test for actions

# =================================================================================================
if __name__ == "__main__":
    unittest.main()

# vim: set tw=0 ai:
