from scapy.all import Ether, Dot1Q, IP, UDP, Raw, sendp, BitField, Packet, wrpcap
import csv
width = 100

def create_pkt(vid,ip_pro,l4_dst_port):
    pkt = Ether(dst="dd:dd:dd:dd:dd:dd",src="cc:cc:cc:cc:cc:cc")/Dot1Q(vlan=vid)/IP(proto=ip_pro)/UDP(dport=l4_dst_port)/"Hello"
    return pkt

def create_send_pkt(port,vid,ip_pro,l4_dst_port):
    print("\n\n")
    print("="*width)
    print(f"Creating and sending packets".center(width))
    print("="*width)
    port = 6
    #Packet for table1 ig_port_loop_tbl
    pkt1 = create_pkt(vid,ip_pro,l4_dst_port)
    sendp(pkt1, iface=f"veth{port* 2}", verbose=False)
    print("\n")  

