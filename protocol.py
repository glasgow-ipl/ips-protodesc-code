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
# Types:

class Type:
    pass

class Nothing(Type):
    def __init__(self):
        self.kind  = "Nothing"
        self.name  = "Nothing"

class Boolean(Type):
    def __init__(self):
        self.kind  = "Boolean"
        self.name  = "Boolean"

class Size(Type):
    def __init__(self):
        self.kind  = "Size"
        self.name  = "Size"

class BitString(Type):
    def __init__(self, name, size):
        self.kind = "BitString"
        self.name = name
        self.size = size

class Array(Type):
    def __init__(self, name, element_type, length):
        self.kind         = "Array"
        self.name         = name
        self.element_type = element_type
        self.length       = length
        if length == None:
            self.size = None
        else:
            self.size = self.length * self.element_type.size

class Struct(Type):
    def __init__(self, name, fields, constraints, actions):
        self.kind        = "Struct"
        self.name        = name
        self.fields      = fields
        self.constraints = constraints
        self.actions     = actions

class Enum(Type):
    def __init__(self, name, variants):
        self.kind     = "Enum"
        self.name     = name
        self.variants = variants

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
        # FIXME: implement this
        # FIXME: This is the return type of self.method on self.target
        print("target = {}".format(self.target.type()))
        raise IRError("unimplemented (MethodInvocationExpression)")

class FunctionInvocationExpression:
    def __init__(self, name, args):
        if re.search(FUNC_NAME_REGEX, name) == None:
            raise IRError("Cannot create expression {}: malformed function name".format(name))
        self.kind   = "FunctionInvocation"
        self.name   = method
        self.args   = args

    def type(self):
        # FIXME: implement this
        raise IRError("unimplemented")

class FieldAccessExpression:
    def __init__(self, target, field):
        self.target = target
        self.field  = field

    def type(self):
        return self.target.type()

class ContextAccessExpression:
    def __init__(self, field):
        self.field = field

    def type(self):
        # FIXME: implement this
        raise IRError("unimplemented (ContextAccessExpression)")

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
    def __init__(self):
        pass

    def type(self):
        # FIXME: implement this
        raise IRError("unimplemented (ThisExpression)")

class ConstantExpression:
    def __init__(self, type_, value):
        self.type_ = type_
        self.value = value

    def type(self):
        return self.type_

# =================================================================================================
# Functions, parameters, and arguments:

class Function:
    def __init__(self, name, parameters, return_type):
        self.name        = name
        self.parameters  = parameters
        self.return_type = return_type

class Parameter:
    def __init__(self, name_, type_):
        self.name = name_
        self.type = type_

class Argument:
    def __init__(self, name_, type_, value_):
        self.name  = name_
        self.type  = type_
        self.value = value_

# =================================================================================================
# Fields in a structure or the context:

class Field:
    def __init__(self, name_, type_, is_present_, transform_):
        self.name       = name_
        self.type       = type_
        self.is_present = is_present_
        self.transform  = transform_

class Transform:
    def __init__(self, into_name, into_type, using):
        self.into_name = into_name
        self.into_type = into_type
        self.using     = using

# =================================================================================================

class Protocol:
    def __init__(self):
        # Types:
        self._types = {}
        self._types["Nothing"] = Nothing()
        self._types["Boolean"] = Boolean()
        self._types["Size"]    = Size()
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

    def _parse_arguments(self, args):
        res = []
        for arg in args:
            name_  = arg["name"]
            expr_  = self._parse_expression(arg["value"])
            type_  = expr_.type()
            # FIXME: what is the value?
            value_ = None
            res.append(Argument(name_, type_, value_))
        return res

    def _parse_expression(self, expr):
        if   expr["expression"] == "MethodInvocation":
            target = self._parse_expression(expr["target"])
            method = expr["method"]
            args   = self._parse_arguments(expr["arguments"])
            return MethodInvocationExpression(target, method, args)
        elif expr["expression"] == "FunctionInvocation":
            name   = self._funcs(expr["name"])
            args   = self._parse_arguments(expr["arguments"])
            return FunctionInvocationExpression(target, methods, args)
        elif expr["expression"] == "FieldAccess":
            target = self._parse_expression(expr["target"])
            field  = expr["field"]
            return FieldAccessExpression(target, field)
        elif expr["expression"] == "ContextAccess":
            field  = expr["field"]
            return ContextAccessExpression(target, field)
        elif expr["expression"] == "IfElse":
            condition = self._parse_expression(expr["condition"])
            if_true   = self._parse_expression(expr["if_true"])
            if_false  = self._parse_expression(expr["if_false"])
            return IfElseExpression(condition, if_true, if_false)
        elif expr["expression"] == "This":
            return ThisExpression()
        elif expr["expression"] == "Constant":
            type_ = self.get_type(expr["type"])
            value = expr["value"]
            return ConstantExpression(type_, value)
        else:
            raise IRError("Cannot parse expression: {}".format(expr["expression"]))
        
    def _parse_transform(self, transform):
        if transform != None:
            into_name = transform["into_name"]
            into_type = self.get_type(transform["into_type"])
            using     = self.get_func(transform["using"])
        else:
            None

    def _parse_fields(self, fields):
        res = []
        for field in fields:
            if re.search(FUNC_NAME_REGEX, field["name"]) == None:
                raise IRError("Cannot parse field {}: malformed name".format(field["name"]))
            _name       = field["name"]
            _type       = self.get_type(field["type"])
            _is_present = self._parse_expression(field["is_present"])
            _transform  = self._parse_transform(field["transform"])
            res.append(Field(_name, _type, _is_present, _transform))
        return res

    def _parse_constraints(self, constraints):
        res = []
        for constraint in constraints:
            expr = self._parse_expression(constraint)
            if expr.type() != self.get_type("Boolean"):
                raise IRError("Cannot parse constraint: {} != Boolean".format(expr.type()))
            res.append(expr)
        return res

    def _parse_actions(self, expression):
        # FIXME: implement this
        raise IRError("unimplemented (_parse_actions)")

    def _parse_variants(self, expression):
        # FIXME: implement this
        raise IRError("unimplemented (_parse_variants)")

    def _parse_parameters(self, parameters):
        res = []
        for p in parameters:
            res.append(Parameter(p["name"], self.get_type(p["type"])))
        return res

    # =============================================================================================
    # Public API:

    def add_bitstring(self, irobj):
        self._validate_irtype(irobj, "BitString")
        name         = irobj["name"]
        size         = irobj["size"]
        self._types[name] = BitString(name, size)

    def add_array(self, irobj):
        self._validate_irtype(irobj, "Array")
        name         = irobj["name"]
        element_type = self._types[irobj["element_type"]]
        length       = irobj["length"]
        self._types[name] = Array(name, element_type, length)

    def add_struct(self, irobj):
        self._validate_irtype(irobj, "Struct")
        name         = irobj["name"]
        fields       = self._parse_fields     (irobj["fields"])
        constraints  = self._parse_constraints(irobj["constraints"])
        actions      = self._parse_actions    (irobj["actions"])
        self._types[name] = Struct(name, fields, constraints, actions)

    def add_enum(self, irobj):
        self._validate_irtype(irobj, "Enum")
        name         = irobj["name"]
        variants     = self._parse_variants(irobj["variants"])
        self._types[name] = Enum(name, variants)

    def add_newtype(self, irobj):
        self._validate_irtype(irobj, "NewType")
        # FIXME: implement this
        raise IRError("unimplemented (add_newtype)")

    def add_function(self, irobj):
        if irobj["construct"] != "Function":
            raise IRError("Cannot create Function from {} object".format(irobj["construct"]))
        if irobj["name"] in self._funcs:
            raise IRError("Cannot create Function {}: already exists".format(irobj["name"]))
        if re.search(FUNC_NAME_REGEX, irobj["name"]) == None:
            raise IRError("Cannot create Function {}: malformed name".format(irobj["name"]))

        name        = irobj["name"]
        params      = self._parse_parameters(irobj["parameters"])
        return_type = self.get_type(irobj["return_type"])
        self._funcs[name] = Function(name, params, return_type)

    def get_type(self, name):
        return self._types[name]

    def get_func(self, name):
        return self._funcs[name]

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
        res = protocol.get_type("Timestamp")
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
        res = protocol.get_type("CSRCList")
        self.assertEqual(res.kind, "Array")
        self.assertEqual(res.name, "CSRCList")
        self.assertEqual(res.element_type, protocol.get_type("SSRC"))
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
        res = protocol.get_type("TestStruct")
        self.assertEqual(res.kind, "Struct")
        self.assertEqual(res.name, "TestStruct")
        self.assertEqual(res.fields[0].name, "seq")
        self.assertEqual(res.fields[0].type, protocol.get_type("SeqNum"))
        # FIXME: add test for fields[0].is_present
        # FIXME: add test for fields[0].transform
        self.assertEqual(res.fields[1].name, "ts")
        self.assertEqual(res.fields[1].type, protocol.get_type("Timestamp"))
        # FIXME: add test for fields[1].is_present
        # FIXME: add test for fields[1].transform
        # FIXME: add test for constraints
        # FIXME: add test for actions

# =================================================================================================
if __name__ == "__main__":
    unittest.main()

# vim: set tw=0 ai:
