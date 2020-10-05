from scapy.all   import *
from scapy.utils import PcapWriter

class Udp(Packet):
    name = "udpheader"
    fields_desc=[BitField("src_port", 33422, 16),
                 BitField("dest_port", 53, 16),
                 BitField("length",  13, 16),
                 BitField("checksum", 0, 16),
                 StrField("payload", "Hello", fmt="c")]

# Generate test pcaps

# UDP - valid
cap = PcapWriter("pcaps/udp-valid-1.pcap")
packet = Udp()
cap.write(packet)

# UDP - bad length value
cap = PcapWriter("pcaps/udp-invalid-badlength.pcap")
packet = Udp(length=7)
cap.write(packet)
