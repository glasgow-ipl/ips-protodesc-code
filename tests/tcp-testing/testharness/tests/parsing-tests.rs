extern crate draft_mcquistin_augmented_tcp_example_00;
extern crate pcap;

use draft_mcquistin_augmented_tcp_example_00::*;
use pcap::Capture;

fn pretty_print_tcp_header(header: &TcpHeader) {
    let mut options : Vec<String> = Vec::new();
    if let Some(hdr_options) = &header.options {
        for option in hdr_options.0.iter() {
            match option {
                TcpOption::EolOption(_opt) => options.push("EOL".to_string()),
                TcpOption::NoopOption(_opt) => options.push("NoOp".to_string()),
                TcpOption::MaximumSegmentSizeOption(opt) => options.push(format!("MSS({:?})", opt.maximum_segment_size.0).to_string()),
                TcpOption::WindowScaleFactorOption(opt) => options.push(format!("WinScale({:?})", opt.window_scale_factor.0).to_string()),
                TcpOption::TimestampOption(opt) => options.push(format!("Timestamp(TSVal: {:?}, TSecr: {:?})", opt.timestamp_value.0, opt.timestamp_echo_reply.0).to_string()),
                TcpOption::SackPermittedOption(_opt) => options.push("SACKPermitted".to_string())
            }
        }
    }
    let options_str = options.join(" ");
    print!("TCP Header\n  src_port: {:?}, dst_port: {:?}\n  seq_num: {:?}, ack_num: {:?}\n  data_offset: {:?}\n  reserved: {:?}, flags: cwr: {:?}, ece: {:?}, urg: {:?}, ack: {:?}, psh: {:?}, rst: {:?}, syn: {:?}, fin: {:?}\n  window size: {:?}\n  checksum: {:?}\n  urgent_pointer: {:?}\n  options: {}\n  payload length: {:?}\n\n", header.source_port.0, header.destination_port.0, header.sequence_number.0, header.acknowledgment_number.0, header.data_offset.0, header.reserved.0, header.cwr.0, header.ece.0, header.urg.0, header.ack.0, header.psh.0, header.rst.0, header.syn.0, header.fin.0, header.window_size.0, header.checksum.0, header.urgent_pointer.0, options_str, header.payload.0.len());
}

#[test]
fn test_parse_tcp_header_10pcap() {
    let mut cap = Capture::from_file("../pcaps/ten_tcp_packets.pcap").unwrap();
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
