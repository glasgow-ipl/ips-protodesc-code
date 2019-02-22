from protocol import *
from output_formatters.json import Json

protocol = Protocol()
protocol.set_protocol_name("test_protocol")

fields = []
constraints = []
actions = []

bitstring_2 = protocol.define_bitstring(
    "BitString$2",
    2
)

bitstring_32 = protocol.define_bitstring(
    "BitString$32",
    32
)

bitstring_variable = protocol.define_bitstring(
    "BitString$variable",
    None
)

fields.append(StructField(
    field_name="version",
    field_type=bitstring_2,
    is_present=None,
    transform=None)
)

fields.append(StructField(
    field_name="payload",
    field_type=bitstring_variable,
    is_present=None,
    transform=None)
)

constraints.append(
    MethodInvocationExpression(
        method_name="eq",
        target=MethodInvocationExpression(
            method_name="size",
            target=FieldAccessExpression(
                target=ThisExpression(),
                field_name="payload"
            ),
            arg_exprs=[]),
        arg_exprs=[
            ArgumentExpression(
                "other",
                IfElseExpression(
                    condition=MethodInvocationExpression(
                        method_name="eq",
                        target=FieldAccessExpression(
                            target=ThisExpression(),
                            field_name="version"
                        ),
                        arg_exprs=[
                            ArgumentExpression(
                                "other",
                                ConstantExpression(
                                    constant_type=bitstring_2,
                                    constant_value=0
                                )
                            )
                        ]),
                    if_true=ConstantExpression(
                        constant_type=protocol.get_type("Size"),
                        constant_value=32
                    ),
                    if_false=ConstantExpression(
                        constant_type=protocol.get_type("Size"),
                        constant_value=64
                    )
                )
            )]
    )
)

protocol.define_struct(
    "test",
    fields,
    constraints,
    actions
)

protocol.define_pdu("test")

output_formatter = Json()
output_formatter.format_protocol(protocol)
print(output_formatter.generate_output())
