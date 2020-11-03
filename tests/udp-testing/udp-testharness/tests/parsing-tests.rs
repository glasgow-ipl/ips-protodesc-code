#[macro_use]
extern crate matches;
extern crate draft_mcquistin_augmented_udp_example_00;
extern crate pcap;

use draft_mcquistin_augmented_udp_example_00::*;
use pcap::Capture;

#[test]
fn test_parse_udp_header_source_port() {
    let data: [u8; 4] = [1, 2, 3, 4];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_udp_header_source_port((&data, 0), &mut context) {
        (Result::Ok(((_, _), source_port)), _) => {
            assert_eq!(source_port.0, 258);
        },
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_udp_header_destination_port() {
    let data: [u8; 4] = [8, 9, 10, 11];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_udp_header_destination_port((&data, 0), &mut context) {
        (Result::Ok(((_, _), dest_port)), _) => {
            assert_eq!(dest_port.0, 2057);
        },
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_udp_header_length() {
    let data: [u8; 4] = [12, 13, 14, 15];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_udp_header_length((&data, 0), &mut context) {
        (Result::Ok(((_, _), length)), _) => {
            assert_eq!(length.0, 3085);
        },
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_udp_header_checksum() {
    let data: [u8; 4] = [16, 17, 18, 19];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_udp_header_checksum((&data, 0), &mut context) {
        (Result::Ok(((_, _), source_port)), _) => {
            assert_eq!(source_port.0, 4113);
        },
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_udp_header_payload() {
    let data: [u8; 4] = [20, 21, 22, 23];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_udp_header_payload((&data, 0), &mut context, 9) {
        (Result::Ok(((_, _), payload)), _) => {
            assert_eq!(payload.0[0], 20);
        },
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_udp_header_payload_badlength() {
    let data: [u8; 4] = [24, 25, 26, 27];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_udp_header_payload((&data, 0), &mut context, 50) {
        (Result::Err(_), _) => {
            assert!(true);
        },
        _ => panic!("Expected error")
    }
}

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

#[test]
fn test_parse_pdu() {
    let mut cap = Capture::from_file("../pcaps/udp-valid-1.pcap").unwrap();
    while let Ok(packet) = cap.next() {
        let mut context = Context { data_size: packet.data.len() as u32 };
        let parsed_pkt = parse_pdu((packet.data, 0), &mut context);
        match parsed_pkt {
            (Result::Ok((_, PDU::UdpHeader(_))), _con) => assert!(true),
            _ => panic!("Invalid packet")
        }
    }
}
