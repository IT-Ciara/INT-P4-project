from scapy.all import Ether, Dot1Q, IP, UDP, Raw, sendp, BitField, Packet, wrpcap
import csv
width = 100

def create_pkt(eth_type):
    pkt = Ether(dst="dd:dd:dd:dd:dd:dd",src="cc:cc:cc:cc:cc:cc",type=eth_type)/"This is polka pkt"
    return pkt

def create_send_pkt(port,eth_type):
    print("\n\n")
    print("="*width)
    print(f"Creating and sending packets".center(width))
    print("="*width)
    port = 6
    #Packet for table1 ig_port_loop_tbl
    pkt1 = create_pkt(eth_type)
    sendp(pkt1, iface=f"veth{port* 2}", verbose=False)
    print("\n")  

