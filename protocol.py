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

from typing import Dict, List, Tuple, Optional
from protocoltypes import *
from expressions import *
from protocoltypeelements import *

from copy import copy

import json
import re

# =================================================================================================

class Protocol:
    _name   : str
    _types  : Dict[str,Type]
    _traits : Dict[str,Trait]
    _funcs  : Dict[str,Function]
    _context: Dict[str, ContextField]
    _pdus   : Dict[str,Type]

    def __init__(self):
        # The protocol is initially unnammed:
        self._name  = None
        # Define the primitive types:
        self._types = {}
        self._types["Nothing"] = Nothing()
        self._types["Boolean"] = Boolean()
        self._types["Size"]    = Size()
        # Define the standard traits:
        self._traits = {}
        self._traits["Value"] = Trait("Value", [
            Function("get", [Parameter("self", None)], None),
            Function("set", [Parameter("self", None), Parameter("value", None)], self.get_type("Nothing"))
        ])
        self._traits["Sized"] = Trait("Sized", [
            Function("size", [Parameter("self", None)], self.get_type("Size"))
        ])
        self._traits["IndexCollection"] = Trait("IndexCollection", [
            Function("get",    [Parameter("self", None), Parameter("index", self.get_type("Size"))], None),
            Function("set",    [Parameter("self", None), Parameter("index", self.get_type("Size")), Parameter("value", None)], self.get_type("Nothing")),
            Function("length", [Parameter("self", None)], self.get_type("Size"))
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
        # Implement standard traits:
        self._types["Boolean"].implement_trait(self.get_trait("Value"))
        self._types["Boolean"].implement_trait(self.get_trait("Equality"))
        self._types["Boolean"].implement_trait(self.get_trait("BooleanOps"))
        self._types["Size"].implement_trait(self.get_trait("Value"))
        self._types["Size"].implement_trait(self.get_trait("Equality"))
        self._types["Size"].implement_trait(self.get_trait("Ordinal"))
        self._types["Size"].implement_trait(self.get_trait("ArithmeticOps"))
        # Define the standards functions:
        self._funcs = {}
        # Define the context:
        self._context = {}
        # Define the PDUs:
        self._pdus = {}

    # =============================================================================================
    # Private helper functions:

    def _validate_irtype(self, irobj, kind):
        if irobj["construct"] != kind:
            raise TypeError("Cannot create {} from {} object".format(kind, irobj["construct"]))
        if irobj["name"] in self._types:
            raise TypeError("Cannot create type {}: already exists".format(irobj["name"]))
        if re.search(TYPE_NAME_REGEX, irobj["name"]) == None:
            raise TypeError("Cannot create type {}: malformed name".format(irobj["name"]))

    def _parse_arguments(self, args, this: Type) -> List[Argument]:
        res = []
        for arg in args:
            name_  = arg["name"]
            value_ = self._parse_expression(arg["value"], this)
            type_  = value_.result_type
            res.append(Argument(name_, type_, value_))
        return res

    def _parse_expression(self, expr, this: Type) -> Expression:
        if not this.kind == "Struct":
            raise TypeError("Expressions can only be evaluated in context of structure types")
        if   expr["expression"] == "MethodInvocation":
            target = self._parse_expression(expr["target"], this)
            method = expr["method"]
            args   = self._parse_arguments(expr["arguments"], this)
            return MethodInvocationExpression(target, method, args)
        elif expr["expression"] == "FunctionInvocation":
            func   = self.get_func(expr["name"])
            args   = self._parse_arguments(expr["arguments"], this)
            return FunctionInvocationExpression(func, args)
        elif expr["expression"] == "FieldAccess":
            target = self._parse_expression(expr["target"], this)
            field  = expr["field"]
            return FieldAccessExpression(target, field)
        elif expr["expression"] == "ContextAccess":
            field  = expr["field"]
            return ContextAccessExpression(self._context, field)
        elif expr["expression"] == "IfElse":
            condition = self._parse_expression(expr["condition"], this)
            if_true   = self._parse_expression(expr["if_true"  ], this)
            if_false  = self._parse_expression(expr["if_false" ], this)
            return IfElseExpression(condition, if_true, if_false)
        elif expr["expression"] == "This":
            return ThisExpression(this)
        elif expr["expression"] == "Constant":
            type_ = self.get_type(expr["type"])
            value = expr["value"]
            return ConstantExpression(type_, value)
        else:
            raise TypeError("Cannot parse expression: {}".format(expr["expression"]))

    def _parse_transform(self, transform) -> Optional[Transform]:
        if transform != None:
            into_name = transform["into_name"]
            into_type = self.get_type(transform["into_type"])
            using     = self.get_func(transform["using"])
            return Transform(into_name, into_type, using)
        else:
            return None

    def _parse_fields(self, fields, this) -> List[StructField]:
        res = []
        for field in fields:
            if re.search(FUNC_NAME_REGEX, field["name"]) == None:
                raise TypeError("Cannot parse field {}: malformed name".format(field["name"]))
            _name       = field["name"]
            _type       = self.get_type(field["type"])
            _is_present = self._parse_expression(field["is_present"], this)
            _transform  = self._parse_transform(field["transform"])
            res.append(StructField(_name, _type, _is_present, _transform))
        return res

    def _parse_constraints(self, constraints, this: Type) -> List[Expression]:
        res = []
        for constraint in constraints:
            expr = self._parse_expression(constraint, this)
            if expr.result_type != self.get_type("Boolean"):
                raise TypeError("Cannot parse constraint: {} != Boolean".format(expr.result_type))
            res.append(expr)
        return res

    def _parse_actions(self, actions, this: Type) -> List[Expression]:
        res = []
        for action in actions:
            expr = self._parse_expression(action, this)
            if expr.result_type != self.get_type("Nothing"):
                raise TypeError("Cannot parse actions: returns {} not Nothing".format(expr.result_type))
            res.append(expr)
        return res

    def _parse_variants(self, variants) -> List[Type]:
        res = []
        for v in variants:
            res.append(self.get_type(v["type"]))
        return res

    def _parse_parameters(self, parameters) -> List[Parameter]:
        res = []
        for p in parameters:
            res.append(Parameter(p["name"], self.get_type(p["type"])))
        return res

    # =============================================================================================
    # Public API:

    def set_protocol_name(self, name: str):
        """
        Define the name of the protocol.

        Parameters:
            self - the protocol in which the new type is defined
            name - the name of the protocol
        """
        if self._name != None:
            raise TypeError("Cannot redefine protocol name")
        self._name = name

    def define_bitstring(self, irobj) -> BitString:
        """
        Define a new bit string type for this protocol. 
        The type constructor is described in Section 3.2.1 of the IR specification.

        Parameters:
            self  - the protocol in which the new type is defined
            irobj - a dict representing the JSON type constructor
        """
        self._validate_irtype(irobj, "BitString")
        name         = irobj["name"]
        size         = irobj["size"]
        self._types[name] = BitString(name, size)
        self._types[name].implement_trait(self.get_trait("Sized"))
        self._types[name].implement_trait(self.get_trait("Value"))
        self._types[name].implement_trait(self.get_trait("Equality"))
        
        return self._types[name]

    def define_array(self, irobj) -> Array:
        """
        Define a new array type for this protocol. 
        The type constructor is described in Section 3.2.2 of the IR specification.

        Parameters:
          self  - the protocol in which the new type is defined
          irobj - a dict representing the JSON type constructor
        """
        self._validate_irtype(irobj, "Array")
        name         = irobj["name"]
        element_type = self._types[irobj["element_type"]]
        length       = irobj["length"]
        self._types[name] = Array(name, element_type, length)
        self._types[name].implement_trait(self.get_trait("Sized"))
        self._types[name].implement_trait(self.get_trait("Equality"))
        self._types[name].implement_trait(self.get_trait("IndexCollection"))
        
        return self._types[name]

    def define_struct(self, irobj) -> Struct:
        """
        Define a new structure type for this protocol. 
        The type constructor is described in Section 3.2.3 of the IR specification.

        Parameters:
          self  - the protocol in which the new type is defined
          irobj - a dict representing the JSON type constructor
        """
        self._validate_irtype(irobj, "Struct")
        name         = irobj["name"]
        self._types[name] = Struct(irobj["name"])
        for field in self._parse_fields(irobj["fields"], self._types[name]):
            self._types[name].add_field(field)
        for constraint in self._parse_constraints(irobj["constraints"], self._types[name]):
            self._types[name].add_constraint(constraint)
        for action in self._parse_actions(irobj["actions"], self._types[name]):
            self._types[name].add_action(action)
        self._types[name].implement_trait(self.get_trait("Sized"))
        self._types[name].implement_trait(self.get_trait("Equality"))
        
        return self._types[name]

    def define_enum(self, irobj) -> Enum:
        """
        Define a new enumerated type for this protocol. 
        The type constructor is described in Section 3.2.4 of the IR specification.

        Parameters:
          self  - the protocol in which the new type is defined
          irobj - a dict representing the JSON type constructor
        """
        self._validate_irtype(irobj, "Enum")
        name         = irobj["name"]
        variants     = self._parse_variants(irobj["variants"])
        self._types[name] = Enum(name, variants)
        self._types[name].implement_trait(self.get_trait("Sized"))
        
        return self._types[name]

    def derive_type(self, irobj) -> "Type":
        """
        Define a new derived type for this protocol. 
        The type constructor is described in Section 3.2.5 of the IR specification.

        Parameters:
          self  - the protocol in which the new type is defined
          irobj - a dict representing the JSON type constructor
        """
        name         = irobj["name"]
        derived_from = irobj["derived_from"]
        implements   = irobj["implements"]
        orig_type    = self.get_type(derived_from)
        self._types[name] = copy(orig_type)
        self._types[name].name    = name
        self._types[name].methods = copy(orig_type.methods)
        for trait_name in orig_type.traits:
        	self._types[name].implement_trait(self.get_trait(trait_name))
        for impl in irobj["implements"]:
            self._types[name].implement_trait(self.get_trait(impl["trait"]))
            
        return self._types[name]

    def define_function(self, irobj) -> Function:
        """
        Define a new function type for this protocol. 
        The type constructor is described in Section 3.2.6 of the IR specification.

        Parameters:
          self  - the protocol in which the new type is defined
          irobj - a dict representing the JSON type constructor
        """
        if irobj["construct"] != "Function":
            raise TypeError("Cannot create Function from {} object".format(irobj["construct"]))
        if irobj["name"] in self._funcs:
            raise TypeError("Cannot create Function {}: already exists".format(irobj["name"]))
        if re.search(FUNC_NAME_REGEX, irobj["name"]) == None:
            raise TypeError("Cannot create Function {}: malformed name".format(irobj["name"]))
        name        = irobj["name"]
        params      = self._parse_parameters(irobj["parameters"])
        return_type = self.get_type(irobj["return_type"])
        self._funcs[name] = Function(name, params, return_type)
        
        return self._funcs[name]

    def define_context(self, irobj):
        """
        Define the context for this protocol.

        Parameters:
          self  - the protocol in which the new type is defined
          irobj - a dict representing the JSON type constructor
        """
        if irobj["construct"] != "Context":
            raise TypeError("Cannot create Context from {} object".format(kind, irobj["construct"]))
        for field in irobj["fields"]:
            _name = field["name"]
            _type = self.get_type(field["type"])
            self._context[_name] = ContextField(_name, _type)

    def define_pdu(self, pdu: str):
        """
        Define a PDU for this protocol.

        Parameters:
          self  - the protocol in which the new type is defined
          pdu   - the name of a pre-existing type that is a PDU
        """
        self._pdus[pdu] = self.get_type(pdu)

    def load(self, protocol_json):
        """
        Load the JSON-formatted representation of a protocol object from a
        string. It might be easier to create a protocol by calling the API
        functions ("define_...()") directly, than by creating a JSON file
        and loading it.

        Arguments:
          protocol_json -- A string containing the JSON form of a protocol object

        Returns:
          Nothing (but updates self to contain the loaded and type-checked IR)
        """
        protocol = json.loads(protocol_json)
        if protocol["construct"] != "Protocol":
            raise IRError("Not a protocol object")
        if re.search(TYPE_NAME_REGEX, protocol["name"]) == None:
            raise IRError("Invalid protocol name: {}".format(name))
        self.set_protocol_name(protocol["name"])
        for obj in protocol["definitions"]:
            if   obj["construct"] == "BitString":
                self.define_bitstring(obj)
            elif obj["construct"] == "Array":
                self.define_array(obj)
            elif obj["construct"] == "Struct":
                self.define_struct(obj)
            elif obj["construct"] == "Enum":
                self.define_enum(obj)
            elif obj["construct"] == "NewType":
                self.derive_type(obj)
            elif obj["construct"] == "Function":
                self.define_function(obj)
            elif obj["construct"] == "Context":
                self.define_context(obj)
            else:
                raise IRError("Cannot load protocol: unknown type constructor " + obj["construct"])
        for pdu in protocol["pdus"]:
            self.define_pdu(pdu["type"])

    def get_protocol_name(self) -> str:
        return self._name

    def get_type(self, type_name: str) -> Type:
        return self._types[type_name]

    def get_func(self, func_name: str) -> Function:
        return self._funcs[func_name]

    def get_trait(self, trait_name: str) -> Trait:
        return self._traits[trait_name]

    def get_context(self):
        return self._context

    def get_pdu(self, pdu_name: str) -> Type:
        return self._pdus[pdu_name]

    def get_pdu_names(self) -> List[str]:
        return list(self._pdus.keys())

# =================================================================================================
# Unit tests:

import unittest

class TestProtocol(unittest.TestCase):
    # =============================================================================================
    # Test cases for types in the IR:

    def test_define_bitstring(self):
        protocol = Protocol()
        protocol.define_bitstring({
            "construct"    : "BitString",
            "name"         : "Timestamp",
            "size"         : 32
        })
        res = protocol.get_type("Timestamp")
        self.assertEqual(res.kind, "BitString")
        self.assertEqual(res.name, "Timestamp")
        self.assertEqual(res.size, 32)
        # Check trait implementations:
        self.assertEqual(len(res.traits), 3)
        self.assertIn("Equality", res.traits)
        self.assertIn("Sized",    res.traits)
        self.assertIn("Value",    res.traits)
        # FIXME: add test for methods

    def test_define_array(self):
        protocol = Protocol()
        protocol.define_bitstring({
            "construct"    : "BitString",
            "name"         : "SSRC",
            "size"         : 32
        })
        protocol.define_array({
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
        # Check trait implementations:
        self.assertEqual(len(res.traits), 3)
        self.assertIn("Equality",        res.traits)
        self.assertIn("IndexCollection", res.traits)
        self.assertIn("Sized",           res.traits)
        # FIXME: add test for methods

    def test_define_struct(self):
        protocol = Protocol()
        protocol.define_bitstring({
            "construct" : "BitString",
            "name"      : "SeqNumTrans",
            "size"      : 16
        })
        protocol.define_bitstring({
            "construct" : "BitString",
            "name"      : "SeqNum",
            "size"      : 16
        })
        protocol.define_bitstring({
            "construct" : "BitString",
            "name"      : "Timestamp",
            "size"      : 32
        })
        protocol.define_function({
            "construct"   : "Function",
            "name"        : "transform_seq",
            "parameters"  : [
            {
                "name" : "seq",
                "type" : "SeqNum"
            }],
            "return_type" : "SeqNumTrans"
        })
        protocol.define_struct({
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
            # FIXME: add tests for actions
            "actions" : [
            ]
        })
        res = protocol.get_type("TestStruct")
        self.assertEqual(res.kind, "Struct")
        self.assertEqual(res.name, "TestStruct")
        self.assertEqual(res.fields[0].field_name, "seq")
        self.assertEqual(res.fields[0].field_type, protocol.get_type("SeqNum"))
        # FIXME: add test for fields[0].is_present
        # FIXME: add test for fields[0].transform
        self.assertEqual(res.fields[1].field_name, "ts")
        self.assertEqual(res.fields[1].field_type, protocol.get_type("Timestamp"))
        # FIXME: add test for fields[1].is_present
        # FIXME: add test for fields[1].transform
        # FIXME: add test for constraints
        # FIXME: add test for actions
        # Check trait implementations:
        self.assertEqual(len(res.traits), 2)
        self.assertIn("Equality", res.traits)
        self.assertIn("Sized",    res.traits)
        # FIXME: add test for methods

    def test_define_enum(self):
        protocol = Protocol()
        protocol.define_bitstring({
            "construct" : "BitString",
            "name"      : "TypeA",
            "size"      : 32
        })
        protocol.define_bitstring({
            "construct" : "BitString",
            "name"      : "TypeB",
            "size"      : 32
        })
        protocol.define_enum({
            "construct"   : "Enum",
            "name"        : "TestEnum",
            "variants"    : [
                {"type" : "TypeA"},
                {"type" : "TypeB"}
            ]
        })
        res = protocol.get_type("TestEnum")
        self.assertEqual(res.variants[0], protocol.get_type("TypeA"))
        self.assertEqual(res.variants[1], protocol.get_type("TypeB"))
        # Check trait implementations:
        self.assertEqual(len(res.traits), 1)
        self.assertIn("Sized", res.traits)
        # FIXME: add test for methods

    def test_derive_type(self):
        protocol = Protocol()
        protocol.define_bitstring({
            "construct" : "BitString",
            "name"      : "Bits16",
            "size"      : 16
        })
        protocol.derive_type({
            "construct"    : "NewType",
            "name"         : "SeqNum",
            "derived_from" : "Bits16",
            "implements"   : [{"trait" : "Ordinal"}]
        })
        res = protocol.get_type("SeqNum")
        self.assertEqual(res.kind, "BitString")
        self.assertEqual(res.name, "SeqNum")
        # Check trait implementations:
        self.assertEqual(len(res.traits), 4)
        self.assertIn("Equality", res.traits)
        self.assertIn("Sized",    res.traits)
        self.assertIn("Value",    res.traits)
        self.assertIn("Ordinal",  res.traits)
        # FIXME: add test for methods

    def test_define_function(self):
        protocol = Protocol()
        protocol.define_bitstring({
            "construct" : "BitString",
            "name"      : "Bits16",
            "size"      : 16
        })
        protocol.define_function({
            "construct"   : "Function",
            "name"        : "testFunction",
            "parameters"  : [
                {
                    "name" : "foo",
                    "type" : "Bits16"
                },
                {
                    "name" : "bar",
                    "type" : "Boolean"
                }
            ],
            "return_type" : "Boolean"
        })
        res = protocol.get_func("testFunction")
        self.assertEqual(res.name, "testFunction")
        self.assertEqual(res.parameters[0].param_name, "foo")
        self.assertEqual(res.parameters[0].param_type, protocol.get_type("Bits16"))
        self.assertEqual(res.parameters[1].param_name, "bar")
        self.assertEqual(res.parameters[1].param_type, protocol.get_type("Boolean"))
        self.assertEqual(res.return_type, protocol.get_type("Boolean"))

    def test_define_context(self):
        protocol = Protocol()
        protocol.define_bitstring({
            "construct" : "BitString",
            "name"      : "Bits16",
            "size"      : 16
        })
        protocol.define_context({
            "construct"   : "Context",
            "fields"  : [
                {
                    "name" : "foo",
                    "type" : "Bits16"
                },
                {
                    "name" : "bar",
                    "type" : "Boolean"
                }
            ]
        })
        self.assertEqual(protocol.get_context()["foo"].field_name, "foo")
        self.assertEqual(protocol.get_context()["foo"].field_type, protocol.get_type("Bits16"))
        self.assertEqual(protocol.get_context()["bar"].field_name, "bar")
        self.assertEqual(protocol.get_context()["bar"].field_type, protocol.get_type("Boolean"))

    # =============================================================================================
    # Test cases for expressions:

    def test_parse_expression_MethodInvocation(self):
        # Expressions must be parsed in the context of a structure type:
        protocol = Protocol()
        protocol.define_struct({
            "construct"   : "Struct",
            "name"        : "TestStruct",
            "fields"      : [],
            "constraints" : [],
            "actions"     : []
        })
        # Check we can parse MethodInvocation expressions:
        json = {
            "expression" : "MethodInvocation",
            "target"     : {
                "expression" : "Constant",
                "type"       : "Boolean",
                "value"      : "True"
            },
            "method"     : "eq",
            "arguments"  : [
                {
                    "name"  : "other",
                    "value" : {
                        "expression" : "Constant",
                        "type"       : "Boolean",
                        "value"      : "False"
                    }
                }
            ]
        }
        expr = protocol._parse_expression(json, protocol.get_type("TestStruct"))
        self.assertTrue(isinstance(expr, MethodInvocationExpression))
        self.assertTrue(expr.result_type, protocol.get_type("Boolean"))

    def test_parse_expression_FunctionInvocation(self):
        # Expressions must be parsed in the context of a structure type:
        protocol = Protocol()
        protocol.define_struct({
            "construct"   : "Struct",
            "name"        : "TestStruct",
            "fields"      : [],
            "constraints" : [],
            "actions"     : []
        })
        protocol.define_bitstring({
            "construct" : "BitString",
            "name"      : "Bits16",
            "size"      : 16
        })
        protocol.define_function({
            "construct"   : "Function",
            "name"        : "testFunction",
            "parameters"  : [
            {
                "name" : "foo",
                "type" : "Bits16"
            },
            {
                "name" : "bar",
                "type" : "Boolean"
            }],
            "return_type" : "Boolean"
        })
        # Check we can parse FunctionInvocation expressions:
        json = {
            "expression" : "FunctionInvocation",
            "name"       : "testFunction",
            "arguments"  : [
                {
                    "name"  : "foo",
                    "value" : {
                        "expression" : "Constant",
                        "type"       : "Bits16",
                        "value"      : 12
                    }
                },
                {
                    "name"  : "bar",
                    "value" : {
                        "expression" : "Constant",
                        "type"       : "Boolean",
                        "value"      : "False"
                    }
                }
            ]
        }
        expr = protocol._parse_expression(json, protocol.get_type("TestStruct"))
        self.assertTrue(isinstance(expr, FunctionInvocationExpression))
        self.assertTrue(expr.result_type, protocol.get_type("Boolean"))

    def test_parse_expression_FieldAccess(self):
        # Expressions must be parsed in the context of a structure type:
        protocol = Protocol()
        protocol.define_bitstring({
            "construct" : "BitString",
            "name"      : "TestField",
            "size"      : 32
        })
        protocol.define_struct({
            "construct"   : "Struct",
            "name"        : "TestStruct",
            "fields"      : [{
                "name"       : "test",
                "type"       : "TestField",
                "is_present" : {
                    "expression" : "Constant",
                    "type"       : "Boolean",
                    "value"      : "True"
                },
                "transform"  : None
            }],
            "constraints" : [],
            "actions"     : []
        })
        # Check that we can parse FieldAccess expressions
        json = {
            "expression" : "FieldAccess",
            "target"     : {"expression" : "This"},
            "field"      : "test"
        }
        expr = protocol._parse_expression(json, protocol.get_type("TestStruct"))
        self.assertTrue(isinstance(expr, FieldAccessExpression))
        self.assertEqual(expr.result_type, protocol.get_type("TestField"))
        self.assertEqual(expr.target.result_type, protocol.get_type("TestStruct"))
        self.assertEqual(expr.field_name, "test")

    def test_parse_expression_ContextAccess(self):
        # Expressions must be parsed in the context of a structure type:
        protocol = Protocol()
        protocol.define_struct({
            "construct"   : "Struct",
            "name"        : "TestStruct",
            "fields"      : [],
            "constraints" : [],
            "actions"     : []
        })
        protocol.define_bitstring({
            "construct" : "BitString",
            "name"      : "Bits16",
            "size"      : 16
        })
        protocol.define_context({
            "construct"   : "Context",
            "fields"  : [
                {
                    "name" : "foo",
                    "type" : "Bits16"
                },
                {
                    "name" : "bar",
                    "type" : "Boolean"
                }
            ]
        })
        # Check that we can parse ContextAccess expressions
        json = {
            "expression" : "ContextAccess",
            "field"      : "foo"
        }
        expr = protocol._parse_expression(json, protocol.get_type("TestStruct"))
        self.assertTrue(isinstance(expr, ContextAccessExpression))
        self.assertEqual(expr.result_type, protocol.get_type("Bits16"))
        self.assertEqual(expr.field_name, "foo")

    def test_parse_expression_IfElse(self):
        # Expressions must be parsed in the context of a structure type:
        protocol = Protocol()
        protocol.define_struct({
            "construct"   : "Struct",
            "name"        : "TestStruct",
            "fields"      : [],
            "constraints" : [],
            "actions"     : []
        })
        # Check we can parse IfElse expressions:
        json = {
            "expression" : "IfElse",
            "condition"  : {
                  "expression" : "Constant",
                  "type"       : "Boolean",
                  "value"      : "True"
            },
            "if_true"    : {
                  "expression" : "Constant",
                  "type"       : "Boolean",
                  "value"      : "True"
            },
            "if_false"   : {
                  "expression" : "Constant",
                  "type"       : "Boolean",
                  "value"      : "False"
            },
        }
        expr = protocol._parse_expression(json, protocol.get_type("TestStruct"))
        self.assertTrue(isinstance(expr, IfElseExpression))
        self.assertEqual(expr.result_type, protocol.get_type("Boolean"))
        self.assertEqual(expr.condition.result_type, protocol.get_type("Boolean"))
        self.assertEqual(expr.if_true.result_type,   protocol.get_type("Boolean"))
        self.assertEqual(expr.if_false.result_type,  protocol.get_type("Boolean"))

    def test_parse_expression_This(self):
        # Expressions must be parsed in the context of a structure type:
        protocol = Protocol()
        protocol.define_struct({
            "construct"   : "Struct",
            "name"        : "TestStruct",
            "fields"      : [],
            "constraints" : [],
            "actions"     : []
        })
        # Check we can parse This expressions:
        json = {
            "expression" : "This"
        }
        expr = protocol._parse_expression(json, protocol.get_type("TestStruct"))
        self.assertTrue(isinstance(expr, ThisExpression))
        self.assertEqual(expr.result_type, protocol.get_type("TestStruct"))

    def test_parse_expression_Constant(self):
        # Expressions must be parsed in the context of a structure type:
        protocol = Protocol()
        protocol.define_struct({
            "construct"   : "Struct",
            "name"        : "TestStruct",
            "fields"      : [],
            "constraints" : [],
            "actions"     : []
        })
        # Check we can parse This expressions:
        json = {
            "expression" : "Constant",
            "type"       : "Size",
            "value"      : 2
        }
        expr = protocol._parse_expression(json, protocol.get_type("TestStruct"))
        self.assertTrue(isinstance(expr, ConstantExpression))
        self.assertTrue(expr.result_type, protocol.get_type("Size"))

    # =============================================================================================
    # Test cases for the overall protocol:

    def test_protocol(self):
        protocol = Protocol()
        # Check the number of built-in types:
        self.assertEqual(len(protocol._types), 3)
        # Check the built-in Nothing type:
        self.assertEqual(protocol.get_type("Nothing").kind, "Nothing")
        self.assertEqual(protocol.get_type("Nothing").name, "Nothing")
        # Check the built-in Boolean type:
        self.assertEqual(protocol.get_type("Boolean").kind, "Boolean")
        self.assertEqual(protocol.get_type("Boolean").name, "Boolean")
        # Check the built-in Size type:
        self.assertEqual(protocol.get_type("Size").kind, "Size")
        self.assertEqual(protocol.get_type("Size").name, "Size")
        # Check the number of built-in traits:
        self.assertEqual(len(protocol._traits), 7)
        # Check the built-in Arithmetic trait:
        self.assertEqual(protocol.get_trait("ArithmeticOps").name, "ArithmeticOps")
        self.assertEqual(protocol.get_trait("ArithmeticOps").methods["plus"    ].name,        "plus")
        self.assertEqual(protocol.get_trait("ArithmeticOps").methods["plus"    ].parameters,  [Parameter("self", None), Parameter("other", None)])
        self.assertEqual(protocol.get_trait("ArithmeticOps").methods["plus"    ].return_type, None)
        self.assertEqual(protocol.get_trait("ArithmeticOps").methods["minus"   ].name,        "minus")
        self.assertEqual(protocol.get_trait("ArithmeticOps").methods["minus"   ].parameters,  [Parameter("self", None), Parameter("other", None)])
        self.assertEqual(protocol.get_trait("ArithmeticOps").methods["minus"   ].return_type, None)
        self.assertEqual(protocol.get_trait("ArithmeticOps").methods["multiply"].name,        "multiply")
        self.assertEqual(protocol.get_trait("ArithmeticOps").methods["multiply"].parameters,  [Parameter("self", None), Parameter("other", None)])
        self.assertEqual(protocol.get_trait("ArithmeticOps").methods["multiply"].return_type, None)
        self.assertEqual(protocol.get_trait("ArithmeticOps").methods["divide"  ].name,        "divide")
        self.assertEqual(protocol.get_trait("ArithmeticOps").methods["divide"  ].parameters,  [Parameter("self", None), Parameter("other", None)])
        self.assertEqual(protocol.get_trait("ArithmeticOps").methods["divide"  ].return_type, None)
        self.assertEqual(protocol.get_trait("ArithmeticOps").methods["modulo"  ].name,        "modulo")
        self.assertEqual(protocol.get_trait("ArithmeticOps").methods["modulo"  ].parameters,  [Parameter("self", None), Parameter("other", None)])
        self.assertEqual(protocol.get_trait("ArithmeticOps").methods["modulo"  ].return_type, None)
        self.assertEqual(len(protocol.get_trait("ArithmeticOps").methods), 5)
        # Check the built-in Boolean trait:
        self.assertEqual(protocol.get_trait("BooleanOps").name, "BooleanOps")
        self.assertEqual(protocol.get_trait("BooleanOps").methods["and"].name,        "and")
        self.assertEqual(protocol.get_trait("BooleanOps").methods["and"].parameters,  [Parameter("self", None), Parameter("other", None)])
        self.assertEqual(protocol.get_trait("BooleanOps").methods["and"].return_type, protocol.get_type("Boolean"))
        self.assertEqual(protocol.get_trait("BooleanOps").methods["or" ].name,        "or")
        self.assertEqual(protocol.get_trait("BooleanOps").methods["or" ].parameters,  [Parameter("self", None), Parameter("other", None)])
        self.assertEqual(protocol.get_trait("BooleanOps").methods["or" ].return_type, protocol.get_type("Boolean"))
        self.assertEqual(protocol.get_trait("BooleanOps").methods["not"].name,        "not")
        self.assertEqual(protocol.get_trait("BooleanOps").methods["not"].parameters,  [Parameter("self", None)])
        self.assertEqual(protocol.get_trait("BooleanOps").methods["not"].return_type, protocol.get_type("Boolean"))
        self.assertEqual(len(protocol.get_trait("BooleanOps").methods), 3)
        # Check the built-in Equality trait:
        self.assertEqual(protocol.get_trait("Equality").name, "Equality")
        self.assertEqual(protocol.get_trait("Equality").methods["eq"].name,        "eq")
        self.assertEqual(protocol.get_trait("Equality").methods["eq"].parameters,  [Parameter("self", None), Parameter("other", None)])
        self.assertEqual(protocol.get_trait("Equality").methods["eq"].return_type, protocol.get_type("Boolean"))
        self.assertEqual(protocol.get_trait("Equality").methods["ne"].name,        "ne")
        self.assertEqual(protocol.get_trait("Equality").methods["ne"].parameters,  [Parameter("self", None), Parameter("other", None)])
        self.assertEqual(protocol.get_trait("Equality").methods["ne"].return_type, protocol.get_type("Boolean"))
        self.assertEqual(len(protocol.get_trait("Equality").methods), 2)
        # Check the built-in Ordinal trait:
        self.assertEqual(protocol.get_trait("Ordinal").name, "Ordinal")
        self.assertEqual(protocol.get_trait("Ordinal").methods["lt"].name,        "lt")
        self.assertEqual(protocol.get_trait("Ordinal").methods["lt"].parameters,  [Parameter("self", None), Parameter("other", None)])
        self.assertEqual(protocol.get_trait("Ordinal").methods["lt"].return_type, protocol.get_type("Boolean"))
        self.assertEqual(protocol.get_trait("Ordinal").methods["le"].name,        "le")
        self.assertEqual(protocol.get_trait("Ordinal").methods["le"].parameters,  [Parameter("self", None), Parameter("other", None)])
        self.assertEqual(protocol.get_trait("Ordinal").methods["le"].return_type, protocol.get_type("Boolean"))
        self.assertEqual(protocol.get_trait("Ordinal").methods["gt"].name,        "gt")
        self.assertEqual(protocol.get_trait("Ordinal").methods["gt"].parameters,  [Parameter("self", None), Parameter("other", None)])
        self.assertEqual(protocol.get_trait("Ordinal").methods["gt"].return_type, protocol.get_type("Boolean"))
        self.assertEqual(protocol.get_trait("Ordinal").methods["ge"].name,        "ge")
        self.assertEqual(protocol.get_trait("Ordinal").methods["ge"].parameters,  [Parameter("self", None), Parameter("other", None)])
        self.assertEqual(protocol.get_trait("Ordinal").methods["ge"].return_type, protocol.get_type("Boolean"))
        self.assertEqual(len(protocol.get_trait("Ordinal").methods), 4)
        # Check the built-in Value trait:
        self.assertEqual(protocol.get_trait("Value").name, "Value")
        self.assertEqual(protocol.get_trait("Value").methods["get"].name,        "get")
        self.assertEqual(protocol.get_trait("Value").methods["get"].parameters,  [Parameter("self", None)])
        self.assertEqual(protocol.get_trait("Value").methods["get"].return_type, None)
        self.assertEqual(protocol.get_trait("Value").methods["set"].name,        "set")
        self.assertEqual(protocol.get_trait("Value").methods["set"].parameters,  [Parameter("self", None), Parameter("value", None)])
        self.assertEqual(protocol.get_trait("Value").methods["set"].return_type, protocol.get_type("Nothing"))
        self.assertEqual(len(protocol.get_trait("Value").methods), 2)
        # Check the built-in Sized trait:
        self.assertEqual(protocol.get_trait("Sized").name, "Sized")
        self.assertEqual(protocol.get_trait("Sized").methods["size"].name,        "size")
        self.assertEqual(protocol.get_trait("Sized").methods["size"].parameters,  [Parameter("self", None)])
        self.assertEqual(protocol.get_trait("Sized").methods["size"].return_type, protocol.get_type("Size"))
        self.assertEqual(len(protocol.get_trait("Sized").methods), 1)
        # Check the built-in IndexCollection trait:
        self.assertEqual(protocol.get_trait("IndexCollection").name, "IndexCollection")
        self.assertEqual(protocol.get_trait("IndexCollection").methods["get"].name,           "get")
        self.assertEqual(protocol.get_trait("IndexCollection").methods["get"].parameters,     [Parameter("self", None), Parameter("index", protocol.get_type("Size"))])
        self.assertEqual(protocol.get_trait("IndexCollection").methods["get"].return_type,    None)
        self.assertEqual(protocol.get_trait("IndexCollection").methods["set"].name,           "set")
        self.assertEqual(protocol.get_trait("IndexCollection").methods["set"].parameters,     [Parameter("self", None), Parameter("index", protocol.get_type("Size")), Parameter("value", None)])
        self.assertEqual(protocol.get_trait("IndexCollection").methods["set"].return_type,    protocol.get_type("Nothing"))
        self.assertEqual(protocol.get_trait("IndexCollection").methods["length"].name,        "length")
        self.assertEqual(protocol.get_trait("IndexCollection").methods["length"].parameters,  [Parameter("self", None)])
        self.assertEqual(protocol.get_trait("IndexCollection").methods["length"].return_type, protocol.get_type("Size"))
        self.assertEqual(len(protocol.get_trait("IndexCollection").methods), 3)

    def test_load(self):
        json = """
            {
                "construct" : "Protocol",
                "name"      : "TestProtocol",
                "definitions" : [
                    {
                        "construct" : "BitString",
                        "name"      : "TypeA",
                        "size"      : 32
                    },
                    {
                        "construct" : "BitString",
                        "name"      : "TypeB",
                        "size"      : 32
                    },
                    {
                        "construct"    : "Array",
                        "name"         : "ArrayTest",
                        "element_type" : "TypeA",
                        "length"       : 4
                    },
                    {
                        "construct"   : "Struct",
                        "name"        : "TestStruct",
                        "fields"      : [],
                        "constraints" : [],
                        "actions"     : []
                    },
                    {
                        "construct"   : "Enum",
                        "name"        : "TestEnum",
                        "variants"    : [
                            {"type" : "TypeA"},
                            {"type" : "TypeB"}
                        ]
                    },
                    {
                        "construct"    : "NewType",
                        "name"         : "FooType",
                        "derived_from" : "TypeA",
                        "implements"   : [{"trait" : "Ordinal"}]
                    }
                ],
                "pdus" : [
                    {"type" : "TestStruct"}
                ]
            }
        """
        protocol = Protocol()
        protocol.load(json)

# =================================================================================================
if __name__ == "__main__":
    unittest.main()

# vim: set tw=0 ai:
