from scapy.all   import *
from scapy.utils import PcapWriter

class SingleFieldHeader(Packet):
    name = "singlefieldheader"
    fields_desc=[BitField("version", 2, 8)]

class MultipleFieldHeader(Packet):
    name = "multiplefieldheader"
    fields_desc=[BitField("version", 3, 8),
                 BitField("field2", 10, 4),
                 BitField("field3",  9, 4)]

# Generate test pcaps

# Single Field Header - valid
cap = PcapWriter("pcaps/sfh-2-valid.pcap")
packet = SingleFieldHeader(version=2)
cap.write(packet)

# Multiple Field Header - valid
cap = PcapWriter("pcaps/mfh-valid.pcap")
packet = MultipleFieldHeader()
cap.write(packet)
