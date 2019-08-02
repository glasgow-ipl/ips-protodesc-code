#[macro_use]
extern crate nom;


enum TestEnum {
    TypeA(u32),
    TypeB(u32),
}


#[derive(Debug, PartialEq, Eq)]
struct SeqNum(u16);

#[derive(Debug, PartialEq, Eq)]
struct SmallStruct {
    seq:  SeqNum,
}


#[derive(Debug, PartialEq, Eq)]
struct Timestamp(u32);

#[derive(Debug, PartialEq, Eq)]
struct Field6(u8);

#[derive(Debug, PartialEq, Eq)]
struct Field10(u16);

#[derive(Debug, PartialEq, Eq)]
struct TestStruct {
    seq:  SeqNum,
    ts:  Timestamp,
    f6:  Field6,
    f10:  Field10,
    nested_struct:     SmallStruct { seq: SeqNum(u16)},
}


fn parse_SmallStruct(wire_data: &[u8]) -> nom::IResult<&[u8], SmallStruct>{
    do_parse!(
    wire_data,
    parsed_data: bits!(tuple!(
        take_bits!(16u8)
    )) >> (SmallStruct {
    seq: SeqNum(parsed_data.0),
    })
)
}


fn parse_TestStruct(wire_data: &[u8]) -> nom::IResult<&[u8], TestStruct>{
    do_parse!(
    wire_data,
    parsed_data: bits!(tuple!(
        take_bits!(16u8),
        take_bits!(32u8),
        take_bits!(6u8),
        take_bits!(10u8),
        take_bits!(16u8)
    )) >> (TestStruct {
    seq: SeqNum(parsed_data.0),
    ts: Timestamp(parsed_data.1),
    f6: Field6(parsed_data.2),
    f10: Field10(parsed_data.3),
    SmallStruct: { seq: SeqNum(parsed_data.4) },
    })
)
}

