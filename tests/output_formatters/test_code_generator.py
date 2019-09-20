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

import sys
sys.path.append('.')

import unittest

from protocol import *

import output_formatters.rust_writer


# =================================================================================================
# Unit tests:

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
        self.assertEqual(len(res.traits), 4)
        self.assertIn("Equality",             res.traits)
        self.assertIn("Sized",                res.traits)
        self.assertIn("Value",                res.traits)
        self.assertIn("IntegerRepresentable", res.traits)
        # FIXME: add test for methods

        #Testing Rust code generation
        generator = output_formatters.rust_writer.RustWriter()
        generator.format_bitstring(res)
        #print("".join(generator.output))

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

        generator = output_formatters.rust_writer.RustWriter()
        generator.format_array(res)
        #print("".join(generator.output))

    def test_write_struct(self):
        protocol = Protocol()

        # define types
        seqnum_trans = protocol.define_bitstring("SeqNumTrans", 16)
        seqnum = protocol.define_bitstring("SeqNum", 16)
        timestamp = protocol.define_bitstring("Timestamp", 32)
        transform_seq = protocol.define_function("transform_seq", [Parameter("seq", seqnum)], seqnum_trans)
        field_6 = protocol.define_bitstring("Field6", 6)
        field_10 = protocol.define_bitstring("Field10", 10)

        ssrc = protocol.define_bitstring("SSRC", 32)
        protocol.define_array("CSRCList", ssrc, 4)
        res_array = protocol.get_type("CSRCList")

        # define fields
        seq = StructField("seq",
                          seqnum,
                          ConstantExpression(protocol.get_type("Boolean"), "True"))
        ts  = StructField("ts",
                          timestamp,
                          None,
                          ConstantExpression(protocol.get_type("Boolean"), "True"))

        f6  = StructField("f6",
                          field_6,
                          None,
                          ConstantExpression(protocol.get_type("Boolean"), "True"))

        f10  = StructField("f10",
                          field_10,
                          None,
                          ConstantExpression(protocol.get_type("Boolean"), "True"))

        array_wrapped = StructField("array_wrapped",
                            res_array,
                            None,
                            ConstantExpression(protocol.get_type("Boolean"), "True"))

        typea = protocol.define_bitstring("TypeA", 32)
        typeb = protocol.define_bitstring("TypeB", 32)
        protocol.define_enum("TestEnum", [typea, typeb])
        res_enum = protocol.get_type("TestEnum")

        enum_field = StructField("enum_field",
                                    res_enum,
                                    None,
                                    ConstantExpression(protocol.get_type("Boolean"), "True"))

        # add constraints
        seq_constraint = MethodInvocationExpression(FieldAccessExpression(SelfExpression(), "seq"),
                                                    "eq",
                                                    [ArgumentExpression("other", ConstantExpression(seqnum, 47))])


        smallstruct = protocol.define_struct("SmallStruct", [seq, f6], [seq_constraint], [])

        nested_struct = StructField("nested_struct",
                                    smallstruct,
                                    None,
                                    ConstantExpression(protocol.get_type("Boolean"), "True"))


        protocol.define_array("StructArray", smallstruct, None)
        struct_array = protocol.get_type("StructArray")

        array_non_wrapped = StructField("array_non_wrapped",
                                        struct_array,
                                        None,
                                        ConstantExpression(protocol.get_type("Boolean"), "True"))

        # construct TestStruct
        #teststruct = protocol.define_struct("TestStruct", [seq, ts, f6, f10, array_wrapped, array_non_wrapped, enum_field], [seq_constraint], [])


        teststruct = protocol.define_struct("TestStruct", [seq, ts, f6, f10, nested_struct], [seq_constraint], [])

        #protocol.define_pdu("TestStruct")

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


    def test_constraints(self):
        protocol = Protocol()
        protocol.set_protocol_name("test_splitfields")

        bit_1 = protocol.define_bitstring(
            "BitString1",
            1
        )

        struct = protocol.define_struct(
            "stun_messagetype_split",
            [
                StructField(
                    field_name="m11",
                    field_type=bit_1,
                    is_present=None,
                ),
                StructField(
                    field_name="m10",
                    field_type=bit_1,
                    is_present=None,
                ),
                StructField(
                    field_name="m9",
                    field_type=bit_1,
                    is_present=None,
                ),
                StructField(
                    field_name="m8",
                    field_type=bit_1,
                    is_present=None,
                ),
                StructField(
                    field_name="m7",
                    field_type=bit_1,
                    is_present=None,
                ),
                StructField(
                    field_name="c1",
                    field_type=bit_1,
                    is_present=None,
                ),
                StructField(
                    field_name="m6",
                    field_type=bit_1,
                    is_present=None,
                ),
                StructField(
                    field_name="m5",
                    field_type=bit_1,
                    is_present=None,
                ),
                StructField(
                    field_name="m4",
                    field_type=bit_1,
                    is_present=None,
                ),
                StructField(
                    field_name="c0",
                    field_type=bit_1,
                    is_present=None,
                ),
                StructField(
                    field_name="m3",
                    field_type=bit_1,
                    is_present=None,
                ),
                StructField(
                    field_name="m2",
                    field_type=bit_1,
                    is_present=None,
                ),
                StructField(
                    field_name="m1",
                    field_type=bit_1,
                    is_present=None,
                ),
                StructField(
                    field_name="m0",
                    field_type=bit_1,
                    is_present=None,
                )
            ],
            [
                MethodInvocationExpression(
                    FieldAccessExpression(SelfExpression(), "m1"),
                    "eq",
                    [
                        ArgumentExpression("other", ConstantExpression(bit_1, "1"))
                    ]
                ),

                MethodInvocationExpression(
                    FieldAccessExpression(SelfExpression(), "c1"),
                    "eq",
                    [
                        ArgumentExpression("other", ConstantExpression(bit_1, "1"))
                    ]
                )
            ],
            []
        )

        protocol.define_pdu("stun_messagetype_split")

        #Testing Rust code generation
        generator = output_formatters.rust_writer.RustWriter()
        generator.format_bitstring(bit_1)
        generator.format_struct(struct)
        generator.format_protocol(protocol)
        #print("".join(generator.output))

    def test_define_enum(self):
        protocol = Protocol()

        seqnum_trans = protocol.define_bitstring("SeqNumTrans", 16)
        seqnum = protocol.define_bitstring("SeqNum", 16)
        redvar = protocol.define_bitstring("Red", 16)
        greenvar = protocol.define_bitstring("Green", 32)
        bluevar = protocol.define_bitstring("Blue", 8)
        combined_var = protocol.define_bitstring("CombinedVar", 32)
        timestamp = protocol.define_bitstring("Timestamp", 32)
        transform_seq = protocol.define_function("transform_seq", [Parameter("seq", seqnum)], seqnum_trans)
        test_function = protocol.define_function("test_function", [Parameter("red", redvar), Parameter("green", greenvar), Parameter("blue", bluevar)], combined_var)
        field_6 = protocol.define_bitstring("Field6", 6)
        field_10 = protocol.define_bitstring("Field10", 10)

        ssrc = protocol.define_bitstring("SSRC", 32)
        protocol.define_array("CSRCList", ssrc, 4)
        res_array = protocol.get_type("CSRCList")

        # define fields
        seq = StructField("seq",
                          seqnum,
                          ConstantExpression(protocol.get_type("Boolean"), "True"))
        ts  = StructField("ts",
                          timestamp,
                          ConstantExpression(protocol.get_type("Boolean"), "True"))

        f6  = StructField("f6",
                          field_6,
                          ConstantExpression(protocol.get_type("Boolean"), "True"))

        f10  = StructField("f10",
                           field_10,
                           ConstantExpression(protocol.get_type("Boolean"), "True"))

        array_wrapped = StructField("array_set_length",
                                    res_array,
                                    ConstantExpression(protocol.get_type("Boolean"), "True"))

        typea = protocol.define_bitstring("TypeA", 32)
        typeb = protocol.define_bitstring("TypeB", 32)
        test_enum = protocol.define_enum("TestEnum", [typea, typeb])
        res_enum = protocol.get_type("TestEnum")

        enum_field = StructField("enum_field",
                                 res_enum,
                                 ConstantExpression(protocol.get_type("Boolean"), "True"))

        # add constraints
        seq_constraint = MethodInvocationExpression(FieldAccessExpression(SelfExpression(), "seq"),
                                                    "eq",
                                                    [ArgumentExpression("other", ConstantExpression(seqnum, 47))])


        smallstruct = protocol.define_struct("SmallStruct", [seq, f6], [seq_constraint], [])

        nested_struct = StructField("nested_struct",
                                    smallstruct,
                                    ConstantExpression(protocol.get_type("Boolean"), "True"))


        protocol.define_array("StructArray", smallstruct, None)
        struct_array = protocol.get_type("StructArray")

        array_non_wrapped = StructField("array_non_fixed_length",
                                        struct_array,
                                        ConstantExpression(protocol.get_type("Boolean"), "True"))

        # construct TestStruct
        teststruct = protocol.define_struct("TestStruct", [seq, ts, f6, f10, array_wrapped, array_non_wrapped, enum_field, nested_struct], [seq_constraint], [])

        res = protocol.get_type("TestEnum")
        self.assertEqual(res.variants[0], protocol.get_type("TypeA"))
        self.assertEqual(res.variants[1], protocol.get_type("TypeB"))
        # Check trait implementations:
        self.assertEqual(len(res.traits), 1)
        self.assertIn("Sized", res.traits)
        # FIXME: add test for methods

        #Testing Rust code generation
        context_bitstring = protocol.define_bitstring("ContextBitstring", 10)
        protocol.define_context_field("ContextTestField", context_bitstring)

        generator = output_formatters.rust_writer.RustWriter()
        generator.format_context(protocol.get_context())
        generator.format_function(transform_seq)
        generator.format_function(test_function)
        generator.format_bitstring(typea)
        generator.format_enum(test_enum)
        generator.format_array(struct_array)
        generator.format_array(res_array)
        generator.format_struct(teststruct)
        print("".join(generator.output))

    def test_derive_type(self):
        protocol = Protocol()
        bits16 = protocol.define_bitstring("Bits16", 16)
        protocol.derive_type("SeqNum", bits16, [protocol.get_trait("Ordinal")])

        res = protocol.get_type("SeqNum")
        self.assertEqual(res.kind, "BitString")
        self.assertEqual(res.name, "SeqNum")
        # Check trait implementations:
        self.assertEqual(len(res.traits), 5)
        self.assertIn("Equality",             res.traits)
        self.assertIn("Sized",                res.traits)
        self.assertIn("Value",                res.traits)
        self.assertIn("Ordinal",              res.traits)
        self.assertIn("IntegerRepresentable", res.traits)
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
                                                    [ArgumentExpression("other", ConstantExpression(protocol.get_type("Boolean"), "False"))])

        self.assertTrue(isinstance(methodinv_expr, MethodInvocationExpression))
        self.assertTrue(methodinv_expr.get_result_type(None), protocol.get_type("Boolean"))

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
        self.assertTrue(funcinv_expr.get_result_type(None), protocol.get_type("Boolean"))

    def test_parse_expression_FieldAccess(self):
        # Expressions must be parsed in the context of a structure type:
        protocol = Protocol()

        testfield = protocol.define_bitstring("TestField", 32)

        # define fields
        test = StructField("test",
                           testfield,
                           None,
                           ConstantExpression(protocol.get_type("Boolean"), "True"))

        teststruct = protocol.define_struct("TestStruct", [test], [], [])

        # Check that we can parse FieldAccess expressions
        fieldaccess_expr = FieldAccessExpression(SelfExpression(), "test")

        self.assertTrue(isinstance(fieldaccess_expr, FieldAccessExpression))
        self.assertEqual(fieldaccess_expr.get_result_type(teststruct), protocol.get_type("TestField"))
        self.assertEqual(fieldaccess_expr.target.get_result_type(teststruct), protocol.get_type("TestStruct"))
        self.assertEqual(fieldaccess_expr.field_name, "test")

    def test_parse_expression_ContextAccess(self):
        protocol = Protocol()

        bits16 = protocol.define_bitstring("Bits16", 16)
        protocol.define_context_field("foo", bits16)
        protocol.define_context_field("bar", protocol.get_type("Boolean"))

        # Check that we can parse ContextAccess expressions
        contextaccess_expr = ContextAccessExpression(protocol.get_context(), "foo")

        self.assertTrue(isinstance(contextaccess_expr, ContextAccessExpression))
        self.assertEqual(contextaccess_expr.get_result_type(None), protocol.get_type("Bits16"))
        self.assertEqual(contextaccess_expr.field_name, "foo")

    def test_parse_expression_IfElse(self):
        protocol = Protocol()

        # Check we can parse IfElse expressions:
        condition = ConstantExpression(protocol.get_type("Boolean"), "True")
        if_true = ConstantExpression(protocol.get_type("Boolean"), "True")
        if_false = ConstantExpression(protocol.get_type("Boolean"), "False")
        ifelse_expr = IfElseExpression(condition, if_true, if_false)

        self.assertTrue(isinstance(ifelse_expr, IfElseExpression))
        self.assertEqual(ifelse_expr.get_result_type(None), protocol.get_type("Boolean"))
        self.assertEqual(ifelse_expr.condition.get_result_type(None), protocol.get_type("Boolean"))
        self.assertEqual(ifelse_expr.if_true.get_result_type(None),   protocol.get_type("Boolean"))
        self.assertEqual(ifelse_expr.if_false.get_result_type(None),  protocol.get_type("Boolean"))

    def test_parse_expression_This(self):
        protocol = Protocol()

        # Check we can parse This expressions:
        teststruct = protocol.define_struct("TestStruct", [], [], [])
        this_expr = SelfExpression()

        self.assertTrue(isinstance(this_expr, SelfExpression))
        self.assertEqual(this_expr.get_result_type(teststruct), protocol.get_type("TestStruct"))

    def test_parse_expression_Constant(self):
        protocol = Protocol()

        # Check we can parse This expressions:
        const_expr = ConstantExpression(protocol.get_type("Size"), 2)

        self.assertTrue(isinstance(const_expr, ConstantExpression))
        self.assertTrue(const_expr.get_result_type(None), protocol.get_type("Size"))

# =================================================================================================
if __name__ == "__main__":
    unittest.main()