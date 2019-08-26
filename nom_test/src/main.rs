extern crate nom;

use nom::IResult; 
use nom::{bits::bits, bits::bytes, bits::complete::take, combinator::map};
use nom::sequence::tuple;
use nom::error::ErrorKind;

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

#[derive(Debug, Eq, PartialEq)]
enum Fruits{
    Orange,
    Mango,
    Lychee,
    Cherry,
}

fn parse_seqnum(input : (&[u8], usize)) -> IResult<(&[u8], usize), SeqNum> {
    map(take(3_usize), |x| SeqNum(x))(input)
}

fn parse_field6(input : (&[u8], usize)) -> IResult<(&[u8], usize), Field6> {
    map(take(6_usize), |x| Field6(x))(input)
}

fn parse_unused2(input : (&[u8], usize)) -> IResult<(&[u8], usize), Unused2> {
    map(take(2_usize), |x| Unused2(x))(input)
}

fn parse_fruits(input : (&[u8], usize)) -> IResult<(&[u8], usize), Option<Fruits>> {
    map(take(2_usize), |x| match x {
        0 => Some(Fruits::Orange),
        1 => Some(Fruits::Mango),
        2 => Some(Fruits::Lychee),
        3 => Some(Fruits::Cherry),
        _ => None,
    })(input)
}

fn parse_mango(input : (&[u8], usize)) -> IResult<(&[u8], usize), Option<Fruits>> {
    map(take(2_usize), |x| match x {
        2 => Ok(Some(Fruits::Mango)),
        _ => Err(nom::Err::Error(("Bad constraint!", ErrorKind::Alt)))
    })(input)

}

fn parse_small_struct(input: (&[u8], usize)) -> nom::IResult<(&[u8], usize), SmallStruct>{
    map(tuple((parse_seqnum, parse_field6, parse_unused2)), |(x, y, z)| SmallStruct{seq: x, f6:y, unused:z})(input)
}

/*
//byte-input function signature
fn parse_small_struct(input: &[u8]) -> nom::IResult<&[u8], SmallStruct>{
    map(bits::<_, _, (_, _), _, _>(tuple((parse_seqnum, parse_field6, parse_unused2))), |(x, y, z)| SmallStruct{seq: x, f6:y, unused:z})(input)
}
*/


#[derive(Debug, PartialEq, Eq)]
struct TestStruct {
    fruit  : Option<Fruits>,
    seq    : SeqNum,
    f6     : Field6,
    smallstruct : SmallStruct
}

/*
fn parse_test_struct(input: &[u8]) -> nom::IResult<&[u8], TestStruct>{
    map(bits::<_, _, (_, _), _, _>(tuple((parse_seqnum, parse_field6, bytes::<_,_,_,(_,_),_>(parse_small_struct)))), |(x, y, z)| TestStruct{seq: x, f6:y, smallstruct:z})(input)
}
*/

/*
fn parse_test_struct(input: &[u8]) -> nom::IResult<&[u8], TestStruct>{
    map(bits::<_, _, (_, _), _, _>(tuple((parse_seqnum, parse_field6, parse_small_struct))), |(x, y, z)| TestStruct{seq: x, f6:y, smallstruct:z})(input)
}
*/

fn parse_test_struct(input: (&[u8], usize)) -> nom::IResult<(&[u8], usize), TestStruct>{
    map(tuple((parse_mango, parse_seqnum, parse_field6, parse_small_struct)), |(w, x, y, z)| TestStruct{fruit: w, seq: x, f6:y, smallstruct:z})(input)
}


fn main() {
    let input = [0b01000010, 0b01111111, 0b10101010, 0b01000110, 0b11001010, 0b11111101, 0b11001011, 0b01011100, 0b00000110, 0b11001010, 0b11111101, 0b11001011, 0b01011100];

    
   match parse_small_struct((&input, 0)) {
        Ok((remain, result)) => {
            println!("Remain: {:?}", remain);
            println!("Result: {:?}", result);
        }
        Err(e) => {
            println!("Failed: {:?}", e)
        }
    }
    
    println!("{:?}", input);

    match parse_test_struct((&input, 0)) {
        Ok((remain, result)) => {
            println!("Remain: {:?}", remain);
            println!("Result: {:?}", result);
        }
        Err(e) => {
            println!("Failed: {:?}", e)
        }
    }
}
