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

ethernet_layer = Ether(dst="00:00:00:00:00:01", src="00:00:00:00:00:02", type=0x88a8)
s_vlan_layer = Dot1Q(vlan=1000, type=0x0601)
int_shim_layer = CustomINTShim(int_count=5, next_hdr=0x8100)
int_layer_0 = CustomINT(data=0x01)
int_layer_1 = CustomINT(data=0x02)
int_layer_2 = CustomINT(data=0x03)
int_layer_3 = CustomINT(data=0x04)
int_layer_4 = CustomINT(data=0x05)

u_vlan_layer = Dot1Q(vlan=10, type=0x800)
ip_layer = IP(src="192.168.122.1", dst="192.168.122.2")
udp_layer = UDP(sport=12345, dport=54321)
payload_layer = Raw(load="This is the payload data")

pkt = ethernet_layer / s_vlan_layer / int_shim_layer / int_layer_0 / int_layer_1 / int_layer_2 / int_layer_3 / int_layer_4 / u_vlan_layer / ip_layer / udp_layer / payload_layer
# pkt = ethernet_layer / s_vlan_layer / int_shim_layer / int_layer_0 / int_layer_1 / int_layer_2 /ip_layer / udp_layer / payload_layer

pkt.show()

#Save the packet to a pcap file
wrpcap("./pcaps/partial_int_stack.pcap", pkt)
sendp(pkt, iface="veth0")