from scapy.all   import *
from scapy.utils import PcapWriter

# ten_tcp_packets.pcap

packets = []

packets.append(Ether() /
               IP(src="10.0.0.2",dst="10.0.0.1") /
               TCP(sport=39898, 
                   dport=5001,
                   seq=1134435089,
                   ack=2154648497,
                   flags='S',
                   options=[('Timestamp', (2028223631, 1113284125)), ('NOP', 0), ('NOP', 0)]))

packets.append(Ether() /
               IP(src="10.0.0.1",dst="10.0.0.2") /
               TCP(sport=5001, 
                   dport=39898,
                   seq=2154648496,
                   ack=1134435090,
                   flags='SA',
                   options=[('MSS', 1460), ('SAckOK', ''), ('Timestamp', (1113284125, 2028223543)), ('NOP', 0), ('WScale', 9)]))

packets.append(Ether() /
               IP(src="10.0.0.2",dst="10.0.0.1") /
               TCP(sport=39898, 
                   dport=5001,
                   seq=1134435090,
                   ack=2154648497,
                   flags='A',
                   options=[('Timestamp', (2028223631, 1113284125)), ('NOP', 0), ('NOP', 0)]))


packets.append(Ether() /
               IP(src="10.0.0.2",dst="10.0.0.1") /
               TCP(sport=39898, 
                   dport=5001,
                   seq=1134435090,
                   ack=2154648497,
                   flags='FA',
                   options=[('Timestamp', (2028223631, 1113284125)), ('NOP', 0), ('NOP', 0)]))

packets.append(Ether() /
               IP(src="10.0.0.1",dst="10.0.0.2") /
               TCP(sport=5001, 
                   dport=39898,
                   seq=2154648497,
                   ack=1134435091,
                   flags='FA',
                   options=[('Timestamp', (1113284215, 2028223631)), ('NOP', 0), ('NOP', 0)]))

packets.append(Ether() /
               IP(src="10.0.0.2",dst="10.0.0.1") /
               TCP(sport=39900, 
                   dport=5001,
                   seq=984389655,
                   ack=0,
                   flags='S',
                   options=[('MSS', 1460), ('SAckOK', ''), ('Timestamp', (2028223633, 0)), ('NOP', 0), ('WScale', 9)]))

packets.append(Ether() /
               IP(src="10.0.0.1",dst="10.0.0.2") /
               TCP(sport=5001, 
                   dport=39900,
                   seq=2011523075,
                   ack=984389656,
                   flags='SA',
                   options=[('MSS', 1460), ('SAckOK', ''), ('Timestamp', (1113284218, 2028223633)), ('NOP', 0), ('WScale', 9)]))

packets.append(Ether() /
               IP(src="10.0.0.2",dst="10.0.0.1") /
               TCP(sport=39898, 
                   dport=5001,
                   seq=1134435091,
                   ack=2154648498,
                   flags='A',
                   options=[('Timestamp', (2028223713, 1113284215)), ('NOP', 0), ('NOP', 0)]))

packets.append(Ether() /
               IP(src="10.0.0.2",dst="10.0.0.1") /
               TCP(sport=39900, 
                   dport=5001,
                   seq=984389656,
                   ack=2011523076,
                   flags='A',
                   options=[('Timestamp', (2028223723, 1113284218)), ('NOP', 0), ('NOP', 0)]))

packets.append(Ether() /
               IP(src="10.0.0.2",dst="10.0.0.1") /
               TCP(sport=39900, 
                   dport=5001,
                   seq=984389656,
                   ack=2011523076,
                   flags='A',
                   options=[('Timestamp', (2028223723, 1113284218)), ('NOP', 0), ('NOP', 0)]))

cap = PcapWriter("pcaps/ten_tcp_packets.pcap")
for packet in packets:
    cap.write(packet)