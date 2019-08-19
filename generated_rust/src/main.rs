extern crate nom;

use nom::{bits::complete::take, combinator::map};
use nom::sequence::tuple;


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
struct TestStruct {
    seq:  SeqNum,
    ts:  Timestamp,
    f6:  Field6,
    f10:  Field10,
    nested_struct: SmallStruct,
}


fn parse_seqnum(input: (&[u8], usize)) -> nom::IResult<(&[u8], usize), SeqNum>{
    map(take(16_usize), |x| SeqNum(x))(input)
}

fn parse_field6(input: (&[u8], usize)) -> nom::IResult<(&[u8], usize), Field6>{
    map(take(6_usize), |x| Field6(x))(input)
}

fn parse_smallstruct(input: (&[u8], usize)) -> nom::IResult<(&[u8], usize), SmallStruct>{
    map(tuple((parse_seqnum, parse_field6)), |(a, b)| SmallStruct{seq: a, f6: b, })(input)
}

fn parse_timestamp(input: (&[u8], usize)) -> nom::IResult<(&[u8], usize), Timestamp>{
    map(take(32_usize), |x| Timestamp(x))(input)
}

fn parse_field10(input: (&[u8], usize)) -> nom::IResult<(&[u8], usize), Field10>{
    map(take(10_usize), |x| Field10(x))(input)
}

fn parse_teststruct(input: (&[u8], usize)) -> nom::IResult<(&[u8], usize), TestStruct>{
    map(tuple((parse_seqnum, parse_timestamp, parse_field6, parse_field10, parse_smallstruct)), |(a, b, c, d, e)| TestStruct{seq: a, ts: b, f6: c, f10: d, nested_struct: e, })(input)
}

//added manually for testing
fn main() {
    let input = [0b01000010, 0b01111111, 0b10101010, 0b01000110, 0b11001010, 0b11111101, 0b11001011, 0b01011100, 0b00000110, 0b11001010, 0b11111101, 0b11001011, 0b01011100];


    match parse_smallstruct((&input, 0)) {
        //match parse_small_struct(&input) {
        Ok((remain, result)) => {
            println!("Remain: {:?}", remain);
            println!("Result: {:?}", result);
        }
        Err(e) => {
            println!("Failed: {:?}", e)
        }
    }

    println!("{:?}", input);

    //match parse_test_struct(&input) {
    match parse_teststruct((&input, 0)) {
        Ok((remain, result)) => {
            println!("Remain: {:?}", remain);
            println!("Result: {:?}", result);
        }
        Err(e) => {
            println!("Failed: {:?}", e)
        }
    }
}