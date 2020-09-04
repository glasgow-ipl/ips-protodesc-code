from scapy.all   import *
from scapy.utils import PcapWriter

class SingleFieldHeader(Packet):
    name = "singlefieldheader"
    fields_desc=[BitField("version", 2, 8)]


# Generate test pcaps

# Single Field Header - valid
cap = PcapWriter("pcaps/sfh-2-valid.pcap")
packet = SingleFieldHeader(version=2)
cap.write(packet)