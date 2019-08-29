extern crate nom;

use nom::{bits::complete::take, combinator::map};
use nom::sequence::tuple;
use nom::error::ErrorKind;
use nom::Err::Error;


#[derive(Debug, PartialEq, Eq)]
struct BitString1(u8);

#[derive(Debug, PartialEq, Eq)]
struct stun_messagetype_split {
    m11: BitString1,
    m10: BitString1,
    m9: BitString1,
    m8: BitString1,
    m7: BitString1,
    c1: BitString1,
    m6: BitString1,
    m5: BitString1,
    m4: BitString1,
    c0: BitString1,
    m3: BitString1,
    m2: BitString1,
    m1: BitString1,
    m0: BitString1,
}

fn parse_bitstring1(input: (&[u8], usize)) -> nom::IResult<(&[u8], usize), BitString1>{

    map(take(1_usize), |x| BitString1(x))(input)
}

fn parse_stun_messagetype_split(input: (&[u8], usize)) -> nom::IResult<(&[u8], usize), stun_messagetype_split>{
    match map(tuple((parse_bitstring1, parse_bitstring1, parse_bitstring1, parse_bitstring1, parse_bitstring1, parse_bitstring1, parse_bitstring1, parse_bitstring1, parse_bitstring1, parse_bitstring1, parse_bitstring1, parse_bitstring1, parse_bitstring1, parse_bitstring1)), |(a, b, c, d, e, f, g, h, i, j, k, l, m, n)| stun_messagetype_split{m11: a, m10: b, m9: c, m8: d, m7: e, c1: f, m6: g, m5: h, m4: i, c0: j, m3: k, m2: l, m1: m, m0: n, })(input) {
        Ok((remain, parsed_value)) =>
            if parsed_value.m1.0 == 1 && parsed_value.c1.0 == 1 {
                Ok((remain, parsed_value))
            } else {
                Err(Error((remain, ErrorKind::Verify)))
            }
        Err(e) => {
            Err(e)
        }
    }
}



//manually added for testing
fn main() {
    let input = [0b01000110, 0b01111111, 0b10101010, 0b01000110, 0b11001010, 0b11111101, 0b11001011, 0b01011100, 0b00000110, 0b11001010, 0b11111101, 0b11001011, 0b01011100, 0b01000110, 0b11001010, 0b11111101, 0b11001011, 0b01000110, 0b11001010, 0b11111101, 0b11001011];


    match parse_stun_messagetype_split((&input, 0)) {
        Ok((remain, result)) => {
            println!("Remain: {:?}", remain);
            println!("Result: {:?}", result);
        }
        Err(e) => {
            println!("Failed: {:?}", e)
        }
    }

    println!("{:?}", input);

}
