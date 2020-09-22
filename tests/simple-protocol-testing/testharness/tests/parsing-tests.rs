extern crate draft_mcquistin_simple_example;
extern crate pcap;

use draft_mcquistin_simple_example::*;
use pcap::Capture;

#[test]
fn test_singlefieldheader_valid() {
  let mut cap = Capture::from_file("../pcaps/sfh-2-valid.pcap").unwrap();
  while let Ok(packet) = cap.next() {
      let mut context = Context { data_size: packet.data.len() as u32 };
      let parsed_pkt = parse_single_field_header((packet.data, 0), &mut context);
      match parsed_pkt {
            (Result::Ok(((x, 0), pkt)), con) => {
                assert_eq!(con.data_size, packet.data.len() as u32);
                assert_eq!(x, []);
                assert_eq!(pkt.version.0, 2);
            },
          _ => panic!("Invalid packet")
      }
  }
}

#[test]
#[should_panic]
fn test_singlefieldheader_valid_unparsed_data() {
  let mut cap = Capture::from_file("../pcaps/mfh-valid.pcap").unwrap();
  while let Ok(packet) = cap.next() {
      let mut context = Context { data_size: packet.data.len() as u32 };
      let parsed_pkt = parse_single_field_header((packet.data, 0), &mut context);
      match parsed_pkt {
          (Result::Ok(((x, 0), pkt)), con) => {
              assert_eq!(con.data_size, packet.data.len() as u32);
              assert_eq!(x, []);
              assert_eq!(pkt.version.0, 3);
            },
          _ => panic!("Invalid packet")
      }
  }
}

#[test]
fn test_multiplefieldheader_valid() {
  let mut cap = Capture::from_file("../pcaps/mfh-valid.pcap").unwrap();
  while let Ok(packet) = cap.next() {
      let mut context = Context { data_size: packet.data.len() as u32 };
      let parsed_pkt = parse_multiple_field_header((packet.data, 0), &mut context);
      match parsed_pkt {
          (Result::Ok(((x, 0), pkt)), con) => {
              assert_eq!(con.data_size, packet.data.len() as u32);
              assert_eq!(x, []);
              assert_eq!(pkt.version.0, 3);
              assert_eq!(pkt.field2.0,  10);
              assert_eq!(pkt.field3.0,  9);
            },
          _ => panic!("Invalid packet")
      }
  }
}

#[test]
#[should_panic]
fn test_multiplefieldheader_not_enough_data() {
  let mut cap = Capture::from_file("../pcaps/sfh-2-valid.pcap").unwrap();
  while let Ok(packet) = cap.next() {
      let mut context = Context { data_size: packet.data.len() as u32 };
      let parsed_pkt = parse_multiple_field_header((packet.data, 0), &mut context);
      match parsed_pkt {
          (Result::Ok(((x, 0), pkt)), con) => {
              assert_eq!(con.data_size, packet.data.len() as u32);
              assert_eq!(x, []);
              assert_eq!(pkt.version.0, 2);
            },
          _ => panic!("Invalid packet")
      }
  }
}

#[test]
fn test_parse_pdu_singlefieldheader() {
    let mut cap = Capture::from_file("../pcaps/sfh-2-valid.pcap").unwrap();
    while let Ok(packet) = cap.next() {
        let mut context = Context { data_size: packet.data.len() as u32 };
        let parsed_pkt = parse_pdu((packet.data, 0), &mut context);
        match parsed_pkt {
            (Result::Ok((_, PDU::SingleFieldHeader(_))), _con) => (),
            _ => panic!("Invalid packet")
        }
    }
}

#[test]
fn test_parse_pdu_multiplefieldheader() {
    let mut cap = Capture::from_file("../pcaps/mfh-valid.pcap").unwrap();
    while let Ok(packet) = cap.next() {
        let mut context = Context { data_size: packet.data.len() as u32 };
        let parsed_pkt = parse_pdu((packet.data, 0), &mut context);
        match parsed_pkt {
            (Result::Ok((_, PDU::MultipleFieldHeader(_))), _con) => (),
            _ => panic!("Invalid packet")
        }
    }
}
