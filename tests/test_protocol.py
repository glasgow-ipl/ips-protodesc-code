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

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import re
from npt.protocol import *


class TestProtocol(unittest.TestCase):
    # =============================================================================================
    # Test cases for types in the IR:

    def test_define_bitstring(self):
        protocol = Protocol()
        ts = BitString("Timestamp", ConstantExpression(Number(), 32))
        protocol.add_type(ts)

        res = protocol.get_type("Timestamp")
        res = cast(BitString, res)
        self.assertEqual(res.name, "Timestamp")
        self.assertEqual(res.size, ConstantExpression(Number(), 32))
        # Check trait implementations:
        self.assertEqual(len(res.traits), 4)
        self.assertIn(Equality(),             res.traits)
        self.assertIn(Sized(),                res.traits)
        self.assertIn(Value(),                res.traits)
        self.assertIn(NumberRepresentable(),  res.traits)
        # FIXME: add test for methods

    def test_define_array(self):
        protocol = Protocol()
        ssrc = BitString("SSRC", ConstantExpression(Number(), 32))
        protocol.add_type(ssrc)
        csrcList = Array("CSRCList", ssrc, ConstantExpression(Number(), 4)) 
        protocol.add_type(csrcList)

        res = protocol.get_type("CSRCList")
        res = cast(Array, res)
        self.assertEqual(res.name, "CSRCList")
        self.assertEqual(res.element_type, protocol.get_type("SSRC"))
        self.assertEqual(res.length, ConstantExpression(Number(), 4))
        self.assertEqual(res.size, MethodInvocationExpression(ConstantExpression(Number(), 32), "mul", [ArgumentExpression("other", ConstantExpression(Number(), 4))]))
        # Check trait implementations:
        self.assertEqual(len(res.traits), 3)
        self.assertIn(Equality(),        res.traits)
        self.assertIn(IndexCollection(), res.traits)
        self.assertIn(Sized(),           res.traits)
        # FIXME: add test for methods

    def test_define_struct(self):
        protocol = Protocol()

        # define types
        seqnum_trans = BitString("SeqNumTrans", ConstantExpression(Number(), 16))
        seqnum = BitString("SeqNum", ConstantExpression(Number(), 16))
        timestamp = BitString("Timestamp", ConstantExpression(Number(), 32))
        transform_seq = Function("transform_seq", [Parameter("seq", seqnum)], seqnum_trans)
        
        protocol.add_type(seqnum_trans)
        protocol.add_type(seqnum)
        protocol.add_type(timestamp)
        protocol.add_type(transform_seq)

        # define fields
        seq = StructField("seq",
                          seqnum,
                          ConstantExpression(Boolean(), "True"))
        ts  = StructField("ts",
                          timestamp,
                          ConstantExpression(Boolean(), "True"))

        # add constraints
        seq_constraint = MethodInvocationExpression(FieldAccessExpression(SelfExpression(), "seq"),
                                                    "eq",
                                                    [ArgumentExpression("other", ConstantExpression(seqnum, 47))])

        # construct TestStruct
        teststruct = protocol.add_type(Struct("TestStruct", [seq, ts], [seq_constraint], []))

        res = protocol.get_type("TestStruct")
        res = cast(Struct, res)
        self.assertEqual(res.name, "TestStruct")
        self.assertEqual(res.get_fields()[0].field_name, "seq")
        self.assertEqual(res.get_fields()[0].field_type, protocol.get_type("SeqNum"))
        # FIXME: add test for fields[0].is_present
        # FIXME: add test for fields[0].transform
        self.assertEqual(res.get_fields()[1].field_name, "ts")
        self.assertEqual(res.get_fields()[1].field_type, protocol.get_type("Timestamp"))
        # FIXME: add test for fields[1].is_present
        # FIXME: add test for fields[1].transform
        # FIXME: add test for constraints
        # FIXME: add test for actions
        # Check trait implementations:
        self.assertEqual(len(res.traits), 2)
        self.assertIn(Equality(), res.traits)
        self.assertIn(Sized(),    res.traits)
        # FIXME: add test for methods

    def test_define_enum(self):
        protocol = Protocol()
        typea = BitString("TypeA", ConstantExpression(Number(), 32))
        typeb = BitString("TypeB", ConstantExpression(Number(), 32))
        protocol.add_type(typea)
        protocol.add_type(typeb)
        protocol.add_type(Enum("TestEnum", [typea, typeb]))

        res = protocol.get_type("TestEnum")
        res = cast(Enum, res)
        self.assertEqual(res.variants[0], protocol.get_type("TypeA"))
        self.assertEqual(res.variants[1], protocol.get_type("TypeB"))
        # Check trait implementations:
        self.assertEqual(len(res.traits), 1)
        self.assertIn(Sized(), res.traits)
        # FIXME: add test for methods

    def test_derive_type(self):
        protocol = Protocol()
        bits16 = BitString("Bits16", ConstantExpression(Number(), 16))
        protocol.add_type(bits16)
        seqnum = bits16.derive_from("SeqNum", [Ordinal()])
        protocol.add_type(seqnum)

        res = protocol.get_type("SeqNum")
        self.assertEqual(res.name, "SeqNum")
        # Check trait implementations:
        self.assertEqual(len(res.traits), 5)
        self.assertIn(Equality(),             res.traits)
        self.assertIn(Sized(),                res.traits)
        self.assertIn(Value(),                res.traits)
        self.assertIn(Ordinal(),              res.traits)
        self.assertIn(NumberRepresentable(),  res.traits)
        # FIXME: add test for methods

    def test_define_function(self):
        protocol = Protocol()
        bits16 = protocol.add_type(BitString("Bits16", ConstantExpression(Number(), 16)))
        protocol.add_type(Function("testFunction",
                                 [Parameter("foo", bits16), Parameter("bar", Boolean())],
                                 Boolean()))

        res = protocol.get_func("testFunction")
        self.assertEqual(res.name, "testFunction")
        self.assertEqual(res.parameters[0].param_name, "foo")
        self.assertEqual(res.parameters[0].param_type, protocol.get_type("Bits16"))
        self.assertEqual(res.parameters[1].param_name, "bar")
        self.assertEqual(res.parameters[1].param_type, Boolean())
        self.assertEqual(res.return_type, Boolean())

    def test_define_context_field(self):
        protocol = Protocol()
        bits16 = protocol.add_type(BitString("Bits16", ConstantExpression(Number(), 16)))
        context = protocol.get_context()
        context.add_field(ContextField("foo", bits16))
        context.add_field(ContextField("bar", Boolean()))

        self.assertEqual(protocol.get_context().field("foo").field_name, "foo")
        self.assertEqual(protocol.get_context().field("foo").field_type, protocol.get_type("Bits16"))
        self.assertEqual(protocol.get_context().field("bar").field_name, "bar")
        self.assertEqual(protocol.get_context().field("bar").field_type, Boolean())

    # =============================================================================================
    # Test cases for expressions:

    def test_parse_expression_MethodInvocation(self):
        protocol = Protocol()

        # Check we can parse MethodInvocation expressions:
        methodinv_expr = MethodInvocationExpression(ConstantExpression(Boolean(), "False"),
                                                    "eq",
                                                    [ArgumentExpression("other", ConstantExpression(Boolean(), "False"))])

        self.assertTrue(isinstance(methodinv_expr, MethodInvocationExpression))
        self.assertTrue(methodinv_expr.result_type(None), Boolean())

    def test_parse_expression_FunctionInvocation(self):
        protocol = Protocol()
        bits16 = protocol.add_type(BitString("Bits16", ConstantExpression(Number(), 16)))
        testfunc = Function("testFunction",
                            [Parameter("foo", bits16), Parameter("bar", Boolean())],
                            Boolean())
        protocol.add_type(testfunc)
                                            

        # Check we can parse FunctionInvocation expressions:
        funcinv_expr = FunctionInvocationExpression(testfunc,
                                                    [ArgumentExpression("foo", ConstantExpression(bits16, 12)),
                                                     ArgumentExpression("bar", ConstantExpression(Boolean(), "False"))])

        self.assertTrue(isinstance(funcinv_expr, FunctionInvocationExpression))
        self.assertTrue(funcinv_expr.result_type(None), Boolean())

    def test_parse_expression_FieldAccess(self):
        # Expressions must be parsed in the context of a structure type:
        protocol = Protocol()

        testfield = BitString("TestField", ConstantExpression(Number(), 32))
        protocol.add_type(testfield)

        # define fields
        test = StructField("test",
                           testfield,
                           ConstantExpression(Boolean(), "True"))

        teststruct = protocol.add_type(Struct("TestStruct", [test], [], []))

        # Check that we can parse FieldAccess expressions
        fieldaccess_expr = FieldAccessExpression(SelfExpression(), "test")

        self.assertTrue(isinstance(fieldaccess_expr, FieldAccessExpression))
        self.assertEqual(fieldaccess_expr.result_type(teststruct), protocol.get_type("TestField"))
        self.assertEqual(fieldaccess_expr.target.result_type(teststruct), protocol.get_type("TestStruct"))
        self.assertEqual(fieldaccess_expr.field_name, "test")

    def test_parse_expression_ContextAccess(self):
        protocol = Protocol()

        bits16 = protocol.add_type(BitString("Bits16", ConstantExpression(Number(), 16)))
        context = protocol.get_context()
        context.add_field(ContextField("foo", bits16))
        context.add_field(ContextField("bar", Boolean()))

        # Check that we can parse ContextAccess expressions
        contextaccess_expr = ContextAccessExpression(protocol.get_context(), "foo")

        self.assertTrue(isinstance(contextaccess_expr, ContextAccessExpression))
        self.assertEqual(contextaccess_expr.result_type(None), protocol.get_type("Bits16"))
        self.assertEqual(contextaccess_expr.field_name, "foo")

    def test_parse_expression_IfElse(self):
        protocol = Protocol()

        # Check we can parse IfElse expressions:
        condition = ConstantExpression(Boolean(), "True")
        if_true = ConstantExpression(Boolean(), "True")
        if_false = ConstantExpression(Boolean(), "False")
        ifelse_expr = IfElseExpression(condition, if_true, if_false)

        self.assertTrue(isinstance(ifelse_expr, IfElseExpression))
        self.assertEqual(ifelse_expr.result_type(None), Boolean())
        self.assertEqual(ifelse_expr.condition.result_type(None), Boolean())
        self.assertEqual(ifelse_expr.if_true.result_type(None),   Boolean())
        self.assertEqual(ifelse_expr.if_false.result_type(None),  Boolean())

    def test_parse_expression_This(self):
        protocol = Protocol()

        # Check we can parse This expressions:
        teststruct = protocol.add_type(Struct("TestStruct", [], [], []))
        this_expr = SelfExpression()

        self.assertTrue(isinstance(this_expr, SelfExpression))
        self.assertEqual(this_expr.result_type(teststruct), protocol.get_type("TestStruct"))

    def test_parse_expression_Constant(self):
        protocol = Protocol()

        # Check we can parse This expressions:
        const_expr = ConstantExpression(Number(), 2)

        self.assertTrue(isinstance(const_expr, ConstantExpression))
        self.assertTrue(const_expr.result_type(None), Number())

# =================================================================================================
if __name__ == "__main__":
    unittest.main()

# vim: set tw=0 ai:
