from protocol import *

protocol = Protocol()
protocol.set_protocol_name("test_splitfields")

bit_1 = protocol.define_bitstring(
    "BitString1",
    1
)

protocol.define_struct(
    "stun_messagetype_split",
    [
        StructField(
            field_name="m11",
            field_type=bit_1,
            is_present=None,
            transform=None
        ),
        StructField(
            field_name="m10",
            field_type=bit_1,
            is_present=None,
            transform=None
        ),
        StructField(
            field_name="m9",
            field_type=bit_1,
            is_present=None,
            transform=None
        ),
        StructField(
            field_name="m8",
            field_type=bit_1,
            is_present=None,
            transform=None
        ),
        StructField(
            field_name="m7",
            field_type=bit_1,
            is_present=None,
            transform=None
        ),
        StructField(
            field_name="c1",
            field_type=bit_1,
            is_present=None,
            transform=None
        ),
        StructField(
            field_name="m6",
            field_type=bit_1,
            is_present=None,
            transform=None
        ),
        StructField(
            field_name="m5",
            field_type=bit_1,
            is_present=None,
            transform=None
        ),
        StructField(
            field_name="m4",
            field_type=bit_1,
            is_present=None,
            transform=None
        ),
        StructField(
            field_name="c0",
            field_type=bit_1,
            is_present=None,
            transform=None
        ),
        StructField(
            field_name="m3",
            field_type=bit_1,
            is_present=None,
            transform=None
        ),
        StructField(
            field_name="m2",
            field_type=bit_1,
            is_present=None,
            transform=None
        ),
        StructField(
            field_name="m1",
            field_type=bit_1,
            is_present=None,
            transform=None
        ),
        StructField(
            field_name="m0",
            field_type=bit_1,
            is_present=None,
            transform=None
        )
    ],
    [
        MethodInvocationExpression(
            FieldAccessExpression(ThisExpression(), "m1"),
            "eq",
            [
               ArgumentExpression("other", ConstantExpression(bit_1, "1"))
            ]
        ),

        MethodInvocationExpression(
            FieldAccessExpression(ThisExpression(), "c1"),
            "eq",
            [
                ArgumentExpression("other", ConstantExpression(bit_1, "1"))
            ]
        )
    ],
    []
)

protocol.define_pdu("stun_messagetype_split")