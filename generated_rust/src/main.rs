extern crate nom;

use nom::{bits::complete::take, combinator::map};
use nom::sequence::tuple;
use nom::error::ErrorKind;
use nom::Err::Error;


#[derive(Debug, PartialEq, Eq)]
struct Field2(u8);

#[derive(Debug, PartialEq, Eq)]
struct Field30(u32);

#[derive(Debug, PartialEq, Eq)]
struct Field64(u64);

#[derive(Debug, PartialEq, Eq)]
struct Field48(u64);

#[derive(Debug, PartialEq, Eq)]
struct Field8(u8);

#[derive(Debug, PartialEq, Eq)]
struct FixedwidthFieldFormat {
    field2: Field2,
    field30: Field30,
    field64: Field64,
    field48: Field48,
    field8: Field8,
}

#[derive(Debug, PartialEq, Eq)]
struct OptionalField(u32);

#[derive(Debug, PartialEq, Eq)]
struct OptionalFieldFormat {
    field8: Field8,
    optionalfield: OptionalField,
}

fn parse_field2(input: (&[u8], usize)) -> nom::IResult<(&[u8], usize), Field2>{
    map(take(2_usize), |x| Field2(x))(input)
}

fn parse_field30(input: (&[u8], usize)) -> nom::IResult<(&[u8], usize), Field30>{
    map(take(30_usize), |x| Field30(x))(input)
}

fn parse_field64(input: (&[u8], usize)) -> nom::IResult<(&[u8], usize), Field64>{
    map(take(64_usize), |x| Field64(x))(input)
}

fn parse_field48(input: (&[u8], usize)) -> nom::IResult<(&[u8], usize), Field48>{
    match map(take(48_usize), |x| Field48(x))(input) {
        Ok((rest, value)) => {
            if value.0 == 2 {
                Ok((rest, value))
            } else {
                Err(Error((rest, ErrorKind::Verify))) // FIXME: unclear what ErrorKind makes sense
            }
        }
        Err(e) => {
            Err(e)
        }
    }
}

fn parse_field8(input: (&[u8], usize)) -> nom::IResult<(&[u8], usize), Field8>{
    map(take(8_usize), |x| Field8(x))(input)
}

fn parse_fixed_width_field_format(input: (&[u8], usize)) -> nom::IResult<(&[u8], usize), FixedwidthFieldFormat>{
    map(tuple((parse_field2, parse_field30, parse_field64, parse_field48, parse_field8)), |(a, b, c, d, e)| FixedwidthFieldFormat{field2: a, field30: b, field64: c, field48: d, field8: e, })(input)
}

fn parse_optionalfield(input: (&[u8], usize)) -> nom::IResult<(&[u8], usize), OptionalField>{
    map(take(32_usize), |x| OptionalField(x))(input)
}

fn parse_optional_field_format(input: (&[u8], usize)) -> nom::IResult<(&[u8], usize), OptionalFieldFormat>{
    map(tuple((parse_field8, parse_optionalfield)), |(a, b)| OptionalFieldFormat{field8: a, optionalfield: b, })(input)
}

//manually added for testing
fn main() {
    let input = [0b01000010, 0b01111111, 0b10101010, 0b01000110, 0b11001010, 0b11111101, 0b11001011, 0b01011100, 0b00000110, 0b11001010, 0b11111101, 0b11001011, 0b01011100, 0b01000110, 0b11001010, 0b11111101, 0b11001011, 0b01000110, 0b11001010, 0b11111101, 0b11001011];


    match parse_fixed_width_field_format((&input, 0)) {
        Ok((remain, result)) => {
            println!("Remain: {:?}", remain);
            println!("Result: {:?}", result);
        }
        Err(e) => {
            println!("Failed: {:?}", e)
        }
    }

    println!("{:?}", input);

    match parse_optional_field_format((&input, 0)) {
        Ok((remain, result)) => {
            println!("Remain: {:?}", remain);
            println!("Result: {:?}", result);
        }
        Err(e) => {
            println!("Failed: {:?}", e)
        }
    }
}
