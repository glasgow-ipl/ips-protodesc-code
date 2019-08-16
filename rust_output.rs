extern crate nom;
use nom::IResult;
use nom::{bits::bits, bits::complete::take, combinator::map};
use nom::sequence::tuple;


enum TestEnum {
    TypeA(u32),
    TypeB(u32),
}


#[derive(Debug, PartialEq, Eq)]
struct SeqNum(u16);

#[derive(Debug, PartialEq, Eq)]
struct Field6(u8);

#[derive(Debug, PartialEq, Eq)]
struct SmallStruct {
    seq:  SeqNum,
    f6:  Field6,
}


#[derive(Debug, PartialEq, Eq)]
struct Timestamp(u32);

#[derive(Debug, PartialEq, Eq)]
struct Field10(u16);

#[derive(Debug, PartialEq, Eq)]
struct SSRC(u32);

#[derive(Debug, PartialEq, Eq)]

#[derive(Debug, PartialEq, Eq)]

enum TestEnum {
    TypeA(u32),
    TypeB(u32),
}

#[derive(Debug, PartialEq, Eq)]
struct TestStruct {
    seq:  SeqNum,
    ts:  Timestamp,
    f6:  Field6,
    f10:  Field10,
    array_wrapped: [SSRC(u32); 4],
    array_non_wrapped: Vec<SmallStruct>,
    enum_field: TestEnum,
}


fn parse_SmallStruct(input: &[u8]) -> nom::IResult<&[u8], SmallStruct>{
    map(bits::<_, _, (_, _), _, _>(tuple(())), || SmallStruct{<zip object at 0x7f1eb8c7a288>})(input)
}

fn parse_TestStruct(input: &[u8]) -> nom::IResult<&[u8], TestStruct>{
    map(bits::<_, _, (_, _), _, _>(tuple(())), || TestStruct{<zip object at 0x7f1eb8c7a288>})(input)
}
