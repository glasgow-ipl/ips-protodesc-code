//TODO: refactor code_generator to produce this - manual alterations have been performed

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
struct SmallStruct2 {
    seq:  u16,
    seq2: u16,
}

#[derive(Debug, PartialEq, Eq)]
struct SmallStruct3 {
    seq:  u16,
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
    nested_struct: SmallStruct,
}


//compiles
fn parse_SmallStruct3(wire_data: &[u8]) -> nom::IResult<&[u8], SmallStruct3>{
//fn parse_SmallStruct(wire_data: &[u8]) {
    do_parse!(
    wire_data,
    parsed_data: bits!(tuple!(
        take_bits!(16u8)
    )) >> (SmallStruct3 {
    seq: parsed_data
    })
)
}

//compiles
fn parse_SmallStruct2(wire_data: &[u8]) -> nom::IResult<&[u8], SmallStruct2>{
//fn parse_SmallStruct(wire_data: &[u8]) {
    do_parse!(
    wire_data,
    parsed_data: bits!(tuple!(
        take_bits!(16u8),
        take_bits!(5u8)
    )) >> (SmallStruct2 {
    seq: parsed_data.0,
    seq2: parsed_data.1
    })
)
}

/*
//does not compile - E0282
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
*/



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
    nested_struct: SmallStruct { seq: SeqNum(parsed_data.4) },
    })
)
}

//manually added for testing
fn main() {
    let input = [0b01000010, 0b01111111, 0b00000000, 0b00000110, 0b11001010, 0b11111101, 0b11001011, 0b01011100, 0b00000110, 0b11001010, 0b11111101, 0b11001011, 0b01011100];
    //let input = [0b01000010, 0b01111111];
    let res = parse_TestStruct(&input);
    println!("{:?}", res);
    //let res = parse_SmallStruct(&input);
    let res = parse_SmallStruct2(&input);
    println!("{:?}", res);
    let res = parse_SmallStruct3(&input);
    println!("{:?}", res);
}