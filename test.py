from protocol import *
from output_formatters.json import Json

protocol = Protocol()
protocol.set_protocol_name("test_protocol")

bitstring_1 = protocol.define_bitstring("BitString$1", 1)
bitstring_2 = protocol.define_bitstring("BitString$2", 2)
bitstring_5 = protocol.define_bitstring("BitString$5", 5)
bitstring_8 = protocol.define_bitstring("BitString$8", 8)
bitstring_16 = protocol.define_bitstring("BitString$16", 16)
bitstring_32 = protocol.define_bitstring("BitString$32", 32)
bitstring_variable = protocol.define_bitstring("BitString$variable", None)

sdes_item_cname = protocol.define_struct(
    name="SDES_Item_CNAME",
    fields=[
        StructField(
            field_name="type",
            field_type=bitstring_8,
            is_present=None,
            transform=None
        ),
        StructField(
            field_name="length",
            field_type=bitstring_8,
            is_present=None,
            transform=None
        ),
        StructField(
            field_name="user_and_domain_name",
            field_type=bitstring_variable,
            is_present=None,
            transform=None
        )
    ],
    constraints=[
        MethodInvocationExpression(
            method_name="eq",
            target=MethodInvocationExpression(
                method_name="size",
                target=FieldAccessExpression(
                    target=ThisExpression(),
                    field_name="user_and_domain_name"
                ),
                arg_exprs=[]
            ),
            arg_exprs=[
                ArgumentExpression(
                    "other",
                    MethodInvocationExpression(
                        method_name="multiply",
                        target=MethodInvocationExpression(
                            method_name="size",
                            target=FieldAccessExpression(
                                target=ThisExpression(),
                                field_name="length"
                            ),
                            arg_exprs=[]
                        ),
                        arg_exprs=[
                            ArgumentExpression(
                                "other",
                                ConstantExpression(
                                    constant_type=protocol.get_type("Integer"),
                                    constant_value=8
                                )
                            )
                        ]
                    )
                )
            ]
        ),
    ],
    actions=[]
)

sdes_item = protocol.define_enum(
    name="SDES_Item",
    variants=[
        sdes_item_cname
    ]
)

sdes_item_array = protocol.define_array(
    name="SDES_Item_Array",
    element_type=sdes_item,
    length=None
)

sdes_chunk = protocol.define_struct(
    name="SDES_Chunk",
    fields=[
        StructField(
            field_name="ssrc_csrc",
            field_type=bitstring_32,
            is_present=None,
            transform=None
        ),
        StructField(
            field_name="sdes_items",
            field_type=sdes_item_array,
            is_present=None,
            transform=None
        )
    ],
    constraints=[],
    actions=[]
)

sdes_chunk_array = protocol.define_array(
    name="SDES_Chunk_Array",
    element_type=sdes_chunk,
    length=None
)

sdes = protocol.define_struct(
    name="SDES",
    fields=[
        StructField(
            field_name="version",
            field_type=bitstring_2,
            is_present=None,
            transform=None
        ),
        StructField(
            field_name="padding",
            field_type=bitstring_1,
            is_present=None,
            transform=None
        ),
        StructField(
            field_name="source_count",
            field_type=bitstring_5,
            is_present=None,
            transform=None
        ),
        StructField(
            field_name="packet_type",
            field_type=bitstring_8,
            is_present=None,
            transform=None
        ),
        StructField(
            field_name="length",
            field_type=bitstring_16,
            is_present=None,
            transform=None
        ),
        StructField(
            field_name="sdes_chunks",
            field_type=sdes_chunk_array,
            is_present=None,
            transform=None
        )
    ],
    constraints=[
        MethodInvocationExpression(
            method_name="eq",
            target=MethodInvocationExpression(
                method_name="to_integer",
                target=FieldAccessExpression(
                    target=ThisExpression(),
                    field_name="version"
                ),
                arg_exprs=[]
            ),
            arg_exprs=[
                ArgumentExpression(
                    "other",
                    ConstantExpression(
                        constant_type=protocol.get_type("Integer"),
                        constant_value=2
                    )
                )
            ]
        ),
        MethodInvocationExpression(
            method_name="eq",
            target=MethodInvocationExpression(
                method_name="length",
                target=FieldAccessExpression(
                    target=ThisExpression(),
                    field_name="sdes_chunks"
                ),
                arg_exprs=[]
            ),
            arg_exprs=[
                ArgumentExpression(
                    "other",
                    MethodInvocationExpression(
                        method_name="to_integer",
                        target=FieldAccessExpression(
                            target=ThisExpression(),
                            field_name="length"
                        ),
                        arg_exprs=[]
                    )
                )
            ]
        )
    ],
    actions=[]
)

protocol.define_pdu("SDES")

output_formatter = Json()
output_formatter.format_protocol(protocol)
print(output_formatter.generate_output())
