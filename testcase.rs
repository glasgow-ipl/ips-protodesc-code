use nom::{bits::complete::take, combinator::map};
use nom::sequence::tuple;
use nom::error::ErrorKind;
use nom::Err::Error;

let mut ContextTestField: u16;
fn transform_seq(seq: SeqNum) -> SeqNumTrans {
    //function body required
    unimplemented!();
}

fn test_function(red: Red, green: Green, blue: Blue) -> CombinedVar {
    //function body required
    unimplemented!();
}


#[derive(Debug, PartialEq, Eq)]
struct TypeA(u32);

enum TestEnum {
    TypeA,
    TypeB,
}

struct StructArray(Vec<SmallStruct>);

struct CSRCList([SSRC(u32); 4]);


#[derive(Debug, PartialEq, Eq)]
struct TestStruct {
    seq: SeqNum,
    ts: Timestamp,
    f6: Field6,
    f10: Field10,
    array_set_length: CSRCList,
    array_non_fixed_length: StructArray,
    enum_field: TestEnum,
    nested_struct: SmallStruct,
}


