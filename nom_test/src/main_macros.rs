#[macro_use]
extern crate nom;

use nom::number::streaming::{be_u8, be_u16};

#[derive(Debug)]
struct TestStruct {
    f1: u8,
    f2: u8,
    f3: u8,
    f4: u8,
    f5: u8,
    f6: u8,
}

//all retrieved bits need to be consumed to avoid compile-time error
//alternatively, add explicit type annotations
//(ie. returns TestStruct, not the unused u8)
fn chain_parsing(i: &[u8]) -> nom::IResult<&[u8], TestStruct>{
       do_parse!(
           i,
           b0: bits!(tuple!(
               take_bits!(1u8),
               take_bits!(2u8),
               take_bits!(9u8)
               ))
           >> b1: bits!(take_bits!(4u8))
           >> b2: bits!(tuple!(
                        take_bits!(3u8),
                        take_bits!(5u8)
                  ))
           >> (TestStruct {
               f1: b0.0,
               f2: b0.1,
               f3: b0.2,
               f4: b1,
               f5: b2.0,
               f6: b2.1,
              })
        )

}


//works, but only reads the first bit - remaining 7 bits are not read
//list of unread input data returned does not contain the byte this operation was performed on
//note: streaming returns incomplete type, complete returns an error type
fn get_single_bit(i: &[u8]) -> nom::IResult<&[u8], &[u8]>{
       nom::bytes::streaming::take(1u8)(i)
}
//macro version of above
named!(take_1_bit<u8>, bits!(take_bits!(1u8)));


//reads x u8s, where x is the value parsed in the first u8
//(this first value is not returned)
//useful for constrained/variable length fields
named!(len_parser, length_data!(be_u8));


//only reads the first x bits from sequential bytes
//ie. 7 bits discarded in first take_bits call, 6 in the second, 1 in the third
named!(take_3<(u8, u8, u8)>, tuple!(bits!(take_bits!(1u8)), bits!(take_bits!(2u8)), bits!(take_bits!(7u8))));


//works, but only for known bit patterns
//not useful for most scenarios
named!(search_pattern<u8>, bits!(tag_bits!(8u8, 0b0010)));


fn main() {
    let input = [0b01000010, 0b01111111, 0b00000000, 0b00000110, 0b11001010, 0b11111101, 0b11001011, 0b01011100];
    let res = chain_parsing(&input);
    println!("{:?}", res);
}
