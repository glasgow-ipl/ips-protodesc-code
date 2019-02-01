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

from copy import copy

import json
import re

# =================================================================================================

class Protocol:
    _name   : str
    _types  : Dict[str,Type]
    _traits : Dict[str,Trait]
    _funcs  : Dict[str,Function]
    _context: Context
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
        self._context = Context()
        # Define the PDUs:
        self._pdus = {}

    # =============================================================================================
    # Private helper functions:

    def _validate_typename(self, name:str):
        if name in self._types:
            raise TypeError("Cannot create type {}: already exists".format(name))
        if re.search(TYPE_NAME_REGEX, name) == None:
            raise TypeError("Cannot create type {}: malformed name".format(name))

    def _validate_fields(self, fields:List[StructField]):
        for field in fields:
            if re.search(FUNC_NAME_REGEX, field.field_name) == None:
                raise TypeError("Cannot parse field {}: malformed name".format(field["name"]))
        return fields

    def _validate_constraints(self, constraints:List[Expression]):
        for constraint in constraints:
            if constraint.result_type != self.get_type("Boolean"):
                raise TypeError("Cannot parse constraint: {} != Boolean".format(constraint.result_type))
        return constraints

    def _validate_actions(self, actions:List[Expression]):
        for action in actions:
            if action.result_type != self.get_type("Nothing"):
                raise TypeError("Cannot parse actions: returns {} not Nothing".format(action.result_type))
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
            raise TypeError("Cannot redefine protocol name")
        self._name = name

    def define_bitstring(self, name:str, size:Size) -> BitString:
        """
        Define a new bit string type for this protocol. 

        Parameters:
          self  - the protocol in which the new type is defined
          name  - the name of the new type
          size  - the size of the new type, in bits
        """
        self._validate_typename(name)
        newtype = BitString(name, size)
        newtype.implement_trait(self.get_trait("Sized"))
        newtype.implement_trait(self.get_trait("Value"))
        newtype.implement_trait(self.get_trait("Equality"))
        self._types[name] = newtype
        return newtype

    def define_array(self, name:str, element_type: Type, length: Size) -> Array:
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

    def define_struct(self, name:str) -> Struct:
        """
        Define a new structure type for this protocol. 

        Parameters:
          self        - the protocol in which the new type is defined
          name        - the name of the new type
        """
        newtype = Struct(name)
        self._types[name] = newtype
        newtype.implement_trait(self.get_trait("Sized"))
        newtype.implement_trait(self.get_trait("Equality"))
        return newtype

    def define_struct_fields(self, struct:Struct, fields:List[StructField]):
        """
        Define the fields of a previously defined Struct.
        
        Parameters:
            self    - the protocol that contains the struct
            struct  - the struct to define the fields for
            fields  - the fields to define in the struct
        """
        for field in self._validate_fields(fields):
            struct.add_field(field)

    def define_struct_constraints(self, struct:Struct, constraints:List[Expression]):
        """
        Define the constraints of a previously defined Struct.
        
        Parameters:
            self         - the protocol that contains the struct
            struct       - the struct to define the constraints for
            constraints  - the constraints to define in the struct
        """
        for constraint in self._validate_constraints(constraints):
            struct.add_constraint(constraint)
            
    def define_struct_actions(self, struct:Struct, actions:List[Expression]):
        """
        Define the actions of a previously defined Struct.
        
        Parameters:
            self     - the protocol that contains the struct
            struct   - the struct to define the actions for
            actions  - the actions to define in the struct
        """
        for action in self._validate_actions(actions):
            struct.add_action(action)

    def define_enum(self, name:str, variants: List[Type]) -> Enum:
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

    def derive_type(self, name: str, derived_from: Type, also_implements: List[Trait]) -> Type:
        """
        Define a new derived type for this protocol. 
        The type constructor is described in Section 3.2.5 of the IR specification.

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

    def define_function(self, name:str, parameters:List[Parameter], return_type:Type) -> Function:
        """
        Define a new function type for this protocol. 

        Parameters:
          self        - the protocol in which the new type is defined
          name        - the name of the new function
          return_type - the type that the function returns
        """
        if name in self._funcs:
            raise TypeError("Cannot create Function {}: already exists".format(name))
        if re.search(FUNC_NAME_REGEX, name) == None:
            raise TypeError("Cannot create Function {}: malformed name".format(name))
        newfunc = Function(name, parameters, return_type)
        self._funcs[name] = newfunc
        return newfunc

    def define_context_field(self, name:str, type:Type):
        """
        Define a context field for this protocol.

        Parameters:
          self   - the protocol whose context is to be added to
          field  - the field to be added
        """
        self._context.add_field(ContextField(name, type))

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
        protocol.define_bitstring("Timestamp", 32)
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
        ssrc = protocol.define_bitstring("SSRC", 32)
        protocol.define_array("CSRCList", ssrc, 4)
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
        
        # define types
        seqnum_trans = protocol.define_bitstring("SeqNumTrans", 16)
        seqnum = protocol.define_bitstring("SeqNum", 16)
        timestamp = protocol.define_bitstring("Timestamp", 32)
        transform_seq = protocol.define_function("transform_seq", [Parameter("seq", seqnum)], seqnum_trans)
        
        # construct TestStruct
        teststruct = protocol.define_struct("TestStruct")
        
        # add fields
        seq = StructField("seq", 
                          seqnum,
                          Transform("ext_seq", seqnum_trans, transform_seq),
                          ConstantExpression(protocol.get_type("Boolean"), "True"))
        ts  = StructField("ts",
                          timestamp,
                          None,
                          ConstantExpression(protocol.get_type("Boolean"), "True"))
        protocol.define_struct_fields(teststruct, [seq, ts])
        
        # add constraints
        seq_constraint = MethodInvocationExpression(FieldAccessExpression(ThisExpression(teststruct), "seq"),
                                                    "eq",
                                                    [Argument("other", seqnum, ConstantExpression(seqnum, 47))])
        protocol.define_struct_constraints(teststruct, [seq_constraint])
        
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
        typea = protocol.define_bitstring("TypeA", 32)
        typeb = protocol.define_bitstring("TypeB", 32)
        protocol.define_enum("TestEnum", [typea, typeb])

        res = protocol.get_type("TestEnum")
        self.assertEqual(res.variants[0], protocol.get_type("TypeA"))
        self.assertEqual(res.variants[1], protocol.get_type("TypeB"))
        # Check trait implementations:
        self.assertEqual(len(res.traits), 1)
        self.assertIn("Sized", res.traits)
        # FIXME: add test for methods

    def test_derive_type(self):
        protocol = Protocol()
        bits16 = protocol.define_bitstring("Bits16", 16)
        protocol.derive_type("SeqNum", bits16, [protocol.get_trait("Ordinal")])
        
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
        bits16 = protocol.define_bitstring("Bits16", 16)
        protocol.define_function("testFunction", 
                                 [Parameter("foo", bits16), Parameter("bar", protocol.get_type("Boolean"))], 
                                 protocol.get_type("Boolean"))

        res = protocol.get_func("testFunction")
        self.assertEqual(res.name, "testFunction")
        self.assertEqual(res.parameters[0].param_name, "foo")
        self.assertEqual(res.parameters[0].param_type, protocol.get_type("Bits16"))
        self.assertEqual(res.parameters[1].param_name, "bar")
        self.assertEqual(res.parameters[1].param_type, protocol.get_type("Boolean"))
        self.assertEqual(res.return_type, protocol.get_type("Boolean"))

    def test_define_context_field(self):
        protocol = Protocol()
        bits16 = protocol.define_bitstring("Bits16", 16)
        protocol.define_context_field("foo", bits16)
        protocol.define_context_field("bar", protocol.get_type("Boolean"))

        self.assertEqual(protocol.get_context().field("foo").field_name, "foo")
        self.assertEqual(protocol.get_context().field("foo").field_type, protocol.get_type("Bits16"))
        self.assertEqual(protocol.get_context().field("bar").field_name, "bar")
        self.assertEqual(protocol.get_context().field("bar").field_type, protocol.get_type("Boolean"))

    # =============================================================================================
    # Test cases for expressions:

    def test_parse_expression_MethodInvocation(self):
        protocol = Protocol()

        # Check we can parse MethodInvocation expressions:
        methodinv_expr = MethodInvocationExpression(ConstantExpression(protocol.get_type("Boolean"), "False"),
                                                    "eq",
                                                    [Argument("other", protocol.get_type("Boolean"), "False")])

        self.assertTrue(isinstance(methodinv_expr, MethodInvocationExpression))
        self.assertTrue(methodinv_expr.result_type, protocol.get_type("Boolean"))

    def test_parse_expression_FunctionInvocation(self):
        protocol = Protocol()
        bits16 = protocol.define_bitstring("Bits16", 16)
        testfunc = protocol.define_function("testFunction",
                                 [Parameter("foo", bits16), Parameter("bar", protocol.get_type("Boolean"))],
                                 protocol.get_type("Boolean"))

        # Check we can parse FunctionInvocation expressions:
        funcinv_expr = FunctionInvocationExpression(testfunc,
                                         [Argument("foo", bits16, 12), 
                                          Argument("bar", protocol.get_type("Boolean"), "False")])

        self.assertTrue(isinstance(funcinv_expr, FunctionInvocationExpression))
        self.assertTrue(funcinv_expr.result_type, protocol.get_type("Boolean"))

    def test_parse_expression_FieldAccess(self):
        # Expressions must be parsed in the context of a structure type:
        protocol = Protocol()
        
        testfield = protocol.define_bitstring("TestField", 32)
        
        teststruct = protocol.define_struct("TestStruct")

        # add fields
        test = StructField("test", 
                           testfield,
                           None,
                           ConstantExpression(protocol.get_type("Boolean"), "True"))
        protocol.define_struct_fields(teststruct, [test])
        

        # Check that we can parse FieldAccess expressions
        fieldaccess_expr = FieldAccessExpression(ThisExpression(teststruct), "test")
        
        self.assertTrue(isinstance(fieldaccess_expr, FieldAccessExpression))
        self.assertEqual(fieldaccess_expr.result_type, protocol.get_type("TestField"))
        self.assertEqual(fieldaccess_expr.target.result_type, protocol.get_type("TestStruct"))
        self.assertEqual(fieldaccess_expr.field_name, "test")

    def test_parse_expression_ContextAccess(self):
        protocol = Protocol()

        bits16 = protocol.define_bitstring("Bits16", 16)
        protocol.define_context_field("foo", bits16)
        protocol.define_context_field("bar", protocol.get_type("Boolean"))
        
        # Check that we can parse ContextAccess expressions
        contextaccess_expr = ContextAccessExpression(protocol.get_context(), "foo")
        
        self.assertTrue(isinstance(contextaccess_expr, ContextAccessExpression))
        self.assertEqual(contextaccess_expr.result_type, protocol.get_type("Bits16"))
        self.assertEqual(contextaccess_expr.field_name, "foo")

    def test_parse_expression_IfElse(self):
        protocol = Protocol()

        # Check we can parse IfElse expressions:
        condition = ConstantExpression(protocol.get_type("Boolean"), "True")
        if_true = ConstantExpression(protocol.get_type("Boolean"), "True")
        if_false = ConstantExpression(protocol.get_type("Boolean"), "False")
        ifelse_expr = IfElseExpression(condition, if_true, if_false)
        
        self.assertTrue(isinstance(ifelse_expr, IfElseExpression))
        self.assertEqual(ifelse_expr.result_type, protocol.get_type("Boolean"))
        self.assertEqual(ifelse_expr.condition.result_type, protocol.get_type("Boolean"))
        self.assertEqual(ifelse_expr.if_true.result_type,   protocol.get_type("Boolean"))
        self.assertEqual(ifelse_expr.if_false.result_type,  protocol.get_type("Boolean"))

    def test_parse_expression_This(self):
        protocol = Protocol()

        # Check we can parse This expressions:
        teststruct = protocol.define_struct("TestStruct")
        this_expr = ThisExpression(teststruct)

        self.assertTrue(isinstance(this_expr, ThisExpression))
        self.assertEqual(this_expr.result_type, protocol.get_type("TestStruct"))

    def test_parse_expression_Constant(self):
        protocol = Protocol()

        # Check we can parse This expressions:
        const_expr = ConstantExpression(protocol.get_type("Size"), 2)

        self.assertTrue(isinstance(const_expr, ConstantExpression))
        self.assertTrue(const_expr.result_type, protocol.get_type("Size"))

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

# =================================================================================================
if __name__ == "__main__":
    unittest.main()

# vim: set tw=0 ai:
