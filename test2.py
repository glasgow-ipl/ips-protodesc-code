from protocol import Protocol, StructField

#       0                   1                   2                   3
#       0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#      |             test 1            |             test 2            |
#      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#      |                            optional                           |
#      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

protocol = Protocol()
protocol.set_protocol_name("protocol")

bitstring_16 = protocol.define_bitstring("BitString$16", 16)
bitstring_32 = protocol.define_bitstring("BitString$32", 32)

protocol.define_struct(
    "struct",
    [
        StructField("test_1", bitstring_16, None, None),
        StructField("test_2", bitstring_16, None, None),
        StructField("test_2", bitstring_16, None, None),
    ],
    [],
    []
)

