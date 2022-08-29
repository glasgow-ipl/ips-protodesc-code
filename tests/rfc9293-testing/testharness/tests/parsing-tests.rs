extern crate rfc9293;
extern crate pcap;

use rfc9293::*;
use pcap::Capture;

fn pretty_print_tcp_header(header: &TcpHeader) {
    let mut options : Vec<String> = Vec::new();
    if let Some(hdr_options) = &header.options {
        for option in hdr_options.0.iter() {
            match option {
                TcpOption::EndOfOptionListOption(_opt) => options.push("EOL".to_string()),
                TcpOption::NoOperationOption(_opt) => options.push("NoOp".to_string()),
                TcpOption::MaximumSegmentSizeOption(opt) => options.push(format!("MSS({:?})", opt.maximum_segment_size.0).to_string()),
            }
        }
    }
    let options_str = options.join(" ");
    print!("TCP Header\n  src_port: {:?}, dst_port: {:?}\n  seq_num: {:?}, ack_num: {:?}\n  data_offset: {:?}\n  reserved: {:?}, flags: cwr: {:?}, ece: {:?}, urg: {:?}, ack: {:?}, psh: {:?}, rst: {:?}, syn: {:?}, fin: {:?}\n  window size: {:?}\n  checksum: {:?}\n  urgent_pointer: {:?}\n  options: {}\n  payload length: {:?}\n\n", header.source_port.0, header.destination_port.0, header.sequence_number.0, header.acknowledgment_number.0, header.data_offset.0, header.reserved.0, header.cwr.0, header.ece.0, header.urg.0, header.ack.0, header.psh.0, header.rst.0, header.syn.0, header.fin.0, header.window.0, header.checksum.0, header.urgent_pointer.0, options_str, header.data.0.len());
}

#[test]
fn test_parse_tcp_header_source_port() {
    let data: [u8; 4] = [1, 2, 3, 4];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_tcp_header_source_port((&data, 0), &mut context) {
        (Result::Ok(((_, _), source_port)), _) => {
            assert_eq!(source_port.0, 258);
        },
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_tcp_header_destination_port() {
    let data: [u8; 4] = [1, 2, 3, 4];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_tcp_header_destination_port((&data, 0), &mut context) {
        (Result::Ok(((_, _), dest_port)), _) => {
            assert_eq!(dest_port.0, 258);
        },
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_tcp_header_sequence_number() {
    let data: [u8; 4] = [1, 2, 3, 4];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_tcp_header_sequence_number((&data, 0), &mut context) {
        (Result::Ok(((_, _), seq_num)), _) => {
            assert_eq!(seq_num.0, 16909060);
        },
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_tcp_header_acknowledgment_number() {
    let data: [u8; 4] = [1, 2, 3, 4];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_tcp_header_acknowledgment_number((&data, 0), &mut context) {
        (Result::Ok(((_, _), ack_num)), _) => {
            assert_eq!(ack_num.0, 16909060);
        },
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_tcp_header_data_offset() {
    let data: [u8; 4] = [16, 2, 3, 4];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_tcp_header_data_offset((&data, 0), &mut context) {
        (Result::Ok(((_, _), doffset)), _) => {
            assert_eq!(doffset.0, 1);
        },
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_tcp_header_reserved() {
    let data: [u8; 4] = [16, 2, 3, 4];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_tcp_header_reserved((&data, 0), &mut context) {
        (Result::Ok(((_, _), reserved)), _) => {
            assert_eq!(reserved.0, 1);
        },
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_tcp_header_cwr() {
    let data: [u8; 4] = [255, 2, 3, 4];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_tcp_header_cwr((&data, 0), &mut context) {
        (Result::Ok(((_, _), cwr)), _) => {
            assert_eq!(cwr.0, 1);
        },
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_tcp_header_ece() {
    let data: [u8; 4] = [255, 2, 3, 4];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_tcp_header_ece((&data, 0), &mut context) {
        (Result::Ok(((_, _), ece)), _) => {
            assert_eq!(ece.0, 1);
        },
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_tcp_header_urg() {
    let data: [u8; 4] = [255, 2, 3, 4];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_tcp_header_urg((&data, 0), &mut context) {
        (Result::Ok(((_, _), urg)), _) => {
            assert_eq!(urg.0, 1);
        },
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_tcp_header_ack() {
    let data: [u8; 4] = [255, 2, 3, 4];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_tcp_header_ack((&data, 0), &mut context) {
        (Result::Ok(((_, _), ack)), _) => {
            assert_eq!(ack.0, 1);
        },
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_tcp_header_psh() {
    let data: [u8; 4] = [255, 2, 3, 4];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_tcp_header_psh((&data, 0), &mut context) {
        (Result::Ok(((_, _), psh)), _) => {
            assert_eq!(psh.0, 1);
        },
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_tcp_header_rst() {
    let data: [u8; 4] = [255, 2, 3, 4];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_tcp_header_rst((&data, 0), &mut context) {
        (Result::Ok(((_, _), rst)), _) => {
            assert_eq!(rst.0, 1);
        },
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_tcp_header_syn() {
    let data: [u8; 4] = [255, 2, 3, 4];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_tcp_header_syn((&data, 0), &mut context) {
        (Result::Ok(((_, _), syn)), _) => {
            assert_eq!(syn.0, 1);
        },
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_tcp_header_fin() {
    let data: [u8; 4] = [255, 2, 3, 4];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_tcp_header_fin((&data, 0), &mut context) {
        (Result::Ok(((_, _), fin)), _) => {
            assert_eq!(fin.0, 1);
        },
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_tcp_header_window() {
    let data: [u8; 4] = [1, 2, 3, 4];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_tcp_header_window((&data, 0), &mut context) {
        (Result::Ok(((_, _), window_size)), _) => {
            assert_eq!(window_size.0, 258);
        },
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_tcp_header_checksum() {
    let data: [u8; 4] = [1, 2, 3, 4];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_tcp_header_checksum((&data, 0), &mut context) {
        (Result::Ok(((_, _), checksum)), _) => {
            assert_eq!(checksum.0, 258);
        },
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_tcp_header_urgent_pointer() {
    let data: [u8; 4] = [1, 2, 3, 4];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_tcp_header_urgent_pointer((&data, 0), &mut context) {
        (Result::Ok(((_, _), urg_pointer)), _) => {
            assert_eq!(urg_pointer.0, 258);
        },
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_end_of_option_list_option_kind() {
    let data: [u8; 4] = [1, 2, 3, 4];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_end_of_option_list_option_kind((&data, 0), &mut context) {
        (Result::Ok(((_, _), option_kind)), _) => {
            assert_eq!(option_kind.0, 1);
        },
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_end_of_option_list_option() {
    let data: [u8; 4] = [0, 2, 3, 4];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_end_of_option_list_option((&data, 0), &mut context) {
        (Result::Ok(((_, _), eol_option)), _) => {
            assert_eq!(eol_option.kind.0, 0);
        },
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_end_of_option_list_option_badkind() {
    let data: [u8; 4] = [1, 2, 3, 4];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_end_of_option_list_option((&data, 0), &mut context) {
        (Result::Err(_), _) => assert!(true),
        _ => panic!("Expected error")
    }
}

#[test]
fn test_parse_no_operation_option_kind() {
    let data: [u8; 4] = [1, 2, 3, 4];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_no_operation_option_kind((&data, 0), &mut context) {
        (Result::Ok(((_, _), option_kind)), _) => {
            assert_eq!(option_kind.0, 1);
        },
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_no_operation_option() {
    let data: [u8; 4] = [1, 2, 3, 4];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_no_operation_option((&data, 0), &mut context) {
        (Result::Ok(((_, _), noop_option)), _) => {
            assert_eq!(noop_option.kind.0, 1);
        },
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_no_operation_option_badkind() {
    let data: [u8; 4] = [0, 2, 3, 4];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_no_operation_option((&data, 0), &mut context) {
        (Result::Err(_), _) => assert!(true),
        _ => panic!("Expected error")
    }
}

#[test]
fn test_parse_maximum_segment_size_option_kind() {
    let data: [u8; 4] = [1, 2, 3, 4];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_maximum_segment_size_option_kind((&data, 0), &mut context) {
        (Result::Ok(((_, _), option_kind)), _) => {
            assert_eq!(option_kind.0, 1);
        },
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_maximum_segment_size_option_length() {
    let data: [u8; 4] = [1, 2, 3, 4];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_maximum_segment_size_option_length((&data, 0), &mut context) {
        (Result::Ok(((_, _), length)), _) => {
            assert_eq!(length.0, 1);
        },
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_maximum_segment_size_option_maximum_segment_size() {
    let data: [u8; 4] = [1, 2, 3, 4];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_maximum_segment_size_option_maximum_segment_size((&data, 0), &mut context) {
        (Result::Ok(((_, _), size)), _) => {
            assert_eq!(size.0, 258);
        },
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_maximum_segment_size_option() {
    let data: [u8; 4] = [2, 4, 1, 2];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_maximum_segment_size_option((&data, 0), &mut context) {
        (Result::Ok(((_, _), mss_option)), _) => {
            assert_eq!(mss_option.kind.0, 2);
            assert_eq!(mss_option.length.0, 4);
            assert_eq!(mss_option.maximum_segment_size.0, 258);
        },
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_maximum_segment_size_option_badkind() {
    let data: [u8; 4] = [0, 2, 3, 4];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_maximum_segment_size_option((&data, 0), &mut context) {
        (Result::Err(_), _) => assert!(true),
        _ => panic!("Expected error")
    }
}

#[test]
fn test_parse_maximum_segment_size_option_badlength() {
    let data: [u8; 4] = [2, 2, 3, 4];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_maximum_segment_size_option((&data, 0), &mut context) {
        (Result::Err(_), _) => assert!(true),
        _ => panic!("Expected error")
    }
}

#[test]
fn test_parse_tcp_option_badkind() {
    let data: [u8; 10] = [12, 10, 1, 2, 3, 4, 1, 2, 3, 4];
    let mut context = Context { data_size: (data.len()*8) as u32 };
    match parse_tcp_option((&data, 0), &mut context) {
        (Result::Err(_), _con) => assert!(true),
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_tcp_header_payload() {
    let data: [u8; 12] = [4, 2, 8, 10, 1, 2, 3, 4, 1, 2, 3, 4];
    let mut context = Context { data_size: ((data.len()*8)+160) as u32 };
    match parse_tcp_header_data((&data, 0), &mut context, 5) {
        (Result::Ok(((_, _), payload)), _) => {
            assert_eq!(payload.0.len(), data.len());
            assert_eq!(payload.0, data);
        },
        _ => panic!("Invalid packet")
    }
}

#[test]
fn test_parse_tcp_header_10pcap() {
    let mut cap = Capture::from_file("../pcaps/tcp-ten-packets.pcap").unwrap();
    let valid_seq_nums = [1134435089, 2154648496, 1134435090, 1134435090, 2154648497, 984389655, 2011523075, 1134435091, 984389656, 984389656];
    let mut count = 0;
    while let Ok(packet) = cap.next() {
        let ip_packet = &packet.data[14..];
        let ip_hdr_len = ip_packet[0] & 0xF;
        let tcp_packet = &ip_packet[(ip_hdr_len*4) as usize..];
        let mut context = Context { data_size: (tcp_packet.len()*8) as u32 };
        let parsed_pkt = parse_tcp_header((tcp_packet, 0), &mut context);
        match parsed_pkt {
            (Result::Ok(((_x, 0), pkt)), _con) => {
                pretty_print_tcp_header(&pkt);
                assert!(valid_seq_nums[count] == pkt.sequence_number.0);
            },
            _ => print!("Invalid packet\n")
        }
        count += 1;
    }
}

#[test]
fn test_parse_pdu_10pcap() {
    let mut cap = Capture::from_file("../pcaps/tcp-ten-packets.pcap").unwrap();
    while let Ok(packet) = cap.next() {
        let ip_packet = &packet.data[14..];
        let ip_hdr_len = ip_packet[0] & 0xF;
        let tcp_packet = &ip_packet[(ip_hdr_len*4) as usize..];
        let mut context = Context { data_size: (tcp_packet.len()*8) as u32 };
        let parsed_pkt = parse_pdu((tcp_packet, 0), &mut context);
        match parsed_pkt {
            (Result::Ok(((_x, 0), pkt)), _con) => assert!(matches!(pkt, PDU::TcpHeader(_))),
            _ => print!("Invalid packet\n")
        }
    }
}
