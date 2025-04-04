from scapy.all import Ether, Dot1Q, IP, UDP, Raw, sendp, BitField, Packet, wrpcap, TCP


def print_layer(layer):
    print(f"Layer: {layer.name}")
    layer.remove_payload()
    layer.show()

def send_pkts(interface, eth_src="00:00:00:00:00:01", eth_dst="00:00:00:00:00:02", eth_type=0x800,
              vlan_id=1, ipv4_src="192.168.230.2", ipv4_dst="192.168.230.3", ipv4_proto=17, 
              l4_dst_port=1000, show_layer=None):

    if vlan_id >1:
        eth_type = 0x8100
    pkt = Ether(src=eth_src, dst=eth_dst, type=eth_type)
    if eth_type == 0x8842 or eth_type == 0x88cc or eth_type == 0x8886:
        pkt = pkt/Raw('PKT')
    else:
        if eth_type == 0x8100 or vlan_id > 1:
            pkt = pkt/Dot1Q(vlan=vlan_id, type=0x800)
        pkt = pkt/IP(src=ipv4_src, dst=ipv4_dst, proto=ipv4_proto)

    if ipv4_proto == 6:
        pkt = pkt/TCP(dport=l4_dst_port)/Raw('hello world')
    else:
        pkt = pkt/UDP(dport=l4_dst_port)/Raw('hello world')

    # Dynamically show only the requested layer
    if show_layer:
        pkt_copy = pkt.copy()   
        for layer in show_layer:
            if layer.lower() == "ether":
                print("Ether")
                l = pkt_copy.copy().getlayer(Ether)
                print_layer(l)
            elif layer.lower() == "ip":
                l = pkt_copy.copy().getlayer(IP)
                print_layer(l)
            elif layer.lower() == "udp" and UDP in pkt:
                l = pkt_copy.copy().getlayer(UDP)
                print_layer(l)
            elif layer.lower() == "tcp" and TCP in pkt:
                l = pkt_copy.copy().getlayer(TCP)
                print_layer(l)
            elif layer.lower() == "dot1q":
                l = pkt_copy.copy().getlayer(Dot1Q)
                print_layer(l)

   
    print(pkt.summary())    
    sendp(pkt, iface=f"veth{interface*2}", verbose=False)





# #Stage 2 
# def basic_pkt(interface):
#     print(f"Sending packet to veth{interface*2}")
#     pkt = Ether(src='00:00:00:00:00:01', dst='00:00:00:00:00:02')/IP(src='192.168.233.5', dst='192.168.234.5')/UDP(sport=1234, dport=5678)/Raw('Stage2')
#     print(pkt.summary())
#     sendp(pkt, iface=f"veth{interface*2}", verbose=False)

# #Stage 3
# def pkt_with_eth_src(src,interface):
#     print(f"Sending packet to veth{interface*2}")
#     pkt = Ether(src=src, dst='00:00:00:00:00:02')/IP(src='192.168.233.5', dst='192.168.234.5')/UDP(sport=1234, dport=5678)/Raw('Stage3')
#     print(pkt.summary())
#     sendp(pkt, iface=f"veth{interface*2}", verbose=False)


# #Stage 4
# def pkt_detailed_pkt(interface,src_eth,eth_dst,eth_type,vlan_id,ipv4_src,ipv4_dst):
#     print(f"Sending packet to veth{interface*2}")
#     pkt = Ether(src=src_eth, dst=eth_dst)/Dot1Q(vlan=vlan_id)/IP(src=ipv4_src, dst=ipv4_dst)/UDP(sport=1234, dport=5678)/Raw('Stage4')
#     print(pkt.summary())
#     sendp(pkt, iface=f"veth{interface*2}", verbose=False)

# #Stage 6
# def pkt_detailed_l4(interface,src_eth,eth_dst,vlan_id,ipv4_src,ipv4_dst,ipv4_proto,l4_src_port,l4_dst_port):
#     print(f"Sending packet to veth{interface*2}")
#     if ipv4_proto == 6:
#         pkt = Ether(src=src_eth, dst=eth_dst)/Dot1Q(vlan=vlan_id)/IP(src=ipv4_src, dst=ipv4_dst)/TCP(sport=l4_src_port, dport=l4_dst_port)/Raw('Stage6')
#     else:
#         pkt = Ether(src=src_eth, dst=eth_dst)/Dot1Q(vlan=vlan_id)/IP(src=ipv4_src, dst=ipv4_dst)/UDP(sport=l4_src_port, dport=l4_dst_port)/Raw('Stage6')
#     print(pkt.summary())
#     sendp(pkt, iface=f"veth{interface*2}", verbose=False)


# #Stage 7
# def pkt_eth_type(interface,eth_type):
#     print(f"Sending packet to veth{interface*2}")
#     if eth_type == 0x8842:
#         pkt = Ether(src='00:00:00:00:00:01', dst='00:00:00:00:00:02', type=0x8842)/Raw('POLKA PKT')
#     else:
#         pkt = Ether(src='00:00:00:00:00:01', dst='00:00:00:00:00:02')/IP(src='192.168.235.2', dst='192.168.235.10')/UDP(sport=1234, dport=5678)/Raw('Stage7')
#     print(pkt.summary())
#     sendp(pkt, iface=f"veth{interface*2}", verbose=False)




    