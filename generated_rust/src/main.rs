extern crate nom;

use nom::IResult; 
use nom::{bits::bits, bits::complete::take, number::complete::be_u16, combinator::map};
use nom::sequence::tuple;

#[derive(Debug, PartialEq, Eq)]
struct SeqNum(u16);

#[derive(Debug, PartialEq, Eq)]
struct Unused2(u8);

#[derive(Debug, PartialEq, Eq)]
struct Field6(u8);

#[derive(Debug, PartialEq, Eq)]
struct SmallStruct {
    seq    : SeqNum,
    f6     : Field6,
    unused : Unused2
}

fn parse_seqnum(input : &[u8]) -> IResult<&[u8], SeqNum> {
    map(be_u16, |x| SeqNum(x))(input)
}

fn parse_field6(input : &[u8]) -> IResult<&[u8], Field6> {
    //map(take(6_usize), |x| Field6(x))(input)
    map(bits::<_, _, (_, _), _, _>(take(6_usize)), |x| Field6(x))(input)
}

fn parse_unused2(input : &[u8]) -> IResult<&[u8], Unused2> {
    //map(take(2_usize), |x| Unused2(x))(input)
    map(bits::<_, _, (_, _), _, _>(take(2_usize)), |x| Unused2(x))(input)
}

fn parse_small_struct(input: &[u8]) -> nom::IResult<&[u8], SmallStruct>{
    map(bits::<_, _, (_, _), _, _>(tuple((parse_seqnum, parse_field6, parse_unused2))), |(x, y, z)| SmallStruct{seq: x, f6:y, unused:z})(input)
    //map(tuple((parse_seqnum, parse_field6, parse_unused2)), |(x, y, z)| SmallStruct{seq: x, f6:y, unused:z})(input)
}


fn main() {
    let input = [0b01000010, 0b01111111, 0b10101010, 0b10000110, 0b11001010, 0b11111101, 0b11001011, 0b01011100, 0b00000110, 0b11001010, 0b11111101, 0b11001011, 0b01011100];

    match parse_seqnum(&input) {
        Ok((remain, result)) => {
            println!("Remain: {:?}", remain);
            println!("Result: {:?}", result);
        }
        Err(e) => {
            println!("Failed: {:?}", e)
        }
    }

    match parse_field6(&input) {
        Ok((remain, result)) => {
            println!("Remain: {:?}", remain);
            println!("Result: {:?}", result);
        }
        Err(e) => {
            println!("Failed: {:?}", e)
        }
    }

    match parse_small_struct(&input) {
        Ok((remain, result)) => {
            println!("Remain: {:?}", remain);
            println!("Result: {:?}", result);
        }
        Err(e) => {
            println!("Failed: {:?}", e)
        }
    }
}
