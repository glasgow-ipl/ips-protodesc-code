#[macro_use]
extern crate matches;
extern crate draft_mcquistin_augmented_udp_example_00;
extern crate pcap;

use draft_mcquistin_augmented_udp_example_00::*;
use pcap::Capture;

#[test]
fn test_parse_udp_header() {
    let mut cap = Capture::from_file("../pcaps/udp-valid-1.pcap").unwrap();
    while let Ok(packet) = cap.next() {
        let mut context = Context { data_size: packet.data.len() as u32 };
        let parsed_pkt = parse_udp_header((packet.data, 0), &mut context);
        match parsed_pkt {
            (Result::Ok(((x, 0), pkt)), con) => {
                assert_eq!(con.data_size, packet.data.len() as u32);
                assert_eq!(x, []);
                assert_eq!(pkt.source_port.0, 33422);
                assert_eq!(pkt.destination_port.0, 53);
                assert_eq!(pkt.length.0, 13);
                assert_eq!(pkt.checksum.0, 0);
                assert_eq!(pkt.payload.0, "Hello".as_bytes());
            },
            _ => panic!("Invalid packet")
        }
    }
}

#[test]
fn test_parse_udp_header_badlength() {
    let mut cap = Capture::from_file("../pcaps/udp-invalid-badlength.pcap").unwrap();
    while let Ok(packet) = cap.next() {
        let mut context = Context { data_size: packet.data.len() as u32 };
        assert!(matches!(parse_udp_header((packet.data, 0), &mut context), (Result::Err(_), _)));
    }
}
