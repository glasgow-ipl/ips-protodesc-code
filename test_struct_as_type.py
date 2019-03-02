from protocol import *
from output_formatters.json import Json

protocol = Protocol()
protocol.set_protocol_name("test_protocol")

bitstring_16 = protocol.define_bitstring("BitString$16", 16)
bitstring_32 = protocol.define_bitstring("BitString$32", 32)
bitstring_variable = protocol.define_bitstring("BitString$variable", None)

header_extension = protocol.define_struct(
    name="header_extension",
    fields=[],
    constraints=[],
    actions=[]
)

protocol.define_struct(
    "test2",
    [
        StructField(
            field_name="header_extension",
            field_type=protocol.get_type("header_extension"),
            is_present=None,
            transform=None
        ),
        StructField(
            field_name="payload",
            field_type=bitstring_32,
            is_present=None,
            transform=None
        )
    ],
    [],
    []
)

header_extension.fields += [
        StructField(
            field_name="defined_by_profile",
            field_type=bitstring_16,
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
            field_name="header_extension",
            field_type=bitstring_variable,
            is_present=None,
            transform=None
        ),
    ]
header_extension.constraints += [
        MethodInvocationExpression(
            method_name="eq",
            target=MethodInvocationExpression(
                method_name="size",
                target=FieldAccessExpression(
                    target=ThisExpression(),
                    field_name="header_extension"
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
        )
    ]

protocol.define_pdu("test2")

output_formatter = Json()
output_formatter.format_protocol(protocol)
print(output_formatter.generate_output())
