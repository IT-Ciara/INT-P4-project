from scapy.all import Ether, Dot1Q, IP, UDP, Raw, sendp, BitField, Packet, wrpcap

# Custom Telemetry Report Header
class CustomINT(Packet):
    name = "CustomINT"
    fields_desc = [
        BitField("data", 0, 32),
    ]

class CustomINTShim(Packet):
    name = "CustomINTShim"
    fields_desc = [
        BitField("stack_full", 0, 1),
        BitField("mtu_full", 0, 1),
        BitField("reserved", 0, 6), # 6 bits reserved
        BitField("int_count", 0, 8),
        BitField("next_hdr", 0x8100, 16)
    ]

int_data = int('1234', 16)  # Convert the hexadecimal string to an integer

ethernet_layer = Ether(dst="00:00:00:00:00:01", src="00:00:00:00:00:02")
ip_layer = IP(src="192.168.122.1", dst="192.168.122.2")
udp_layer = UDP(sport=12345, dport=54321)
#Make the packet to be 10,500 bytes
payload_layer = Raw(load="A"*10000)


pkt = ethernet_layer / ip_layer / udp_layer / payload_layer

pkt.show()

#Save the packet to a pcap file
wrpcap("./pcaps/full_mtu.pcap", pkt)
sendp(pkt, iface="veth0")
