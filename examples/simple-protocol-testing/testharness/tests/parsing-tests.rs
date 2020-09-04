extern crate draft_mcquistin_simple_example;
extern crate pcap;

use draft_mcquistin_simple_example::*;
use pcap::Capture;

#[test]
fn test_singlefieldheader_valid() {
  let mut cap = Capture::from_file("../pcaps/sfh-2-valid.pcap").unwrap();
  while let Ok(packet) = cap.next() {
      let parsed_pkt = parse_single_field_header((packet.data, 0));
      match parsed_pkt {
          Result::Ok((_, pkt)) => { 
              assert_eq!(pkt.version.0, 2);
            },
          _ => panic!("Invalid packet")
      }
  }
}