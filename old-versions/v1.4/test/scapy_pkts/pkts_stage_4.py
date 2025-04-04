from scapy.all import Ether, Dot1Q, IP, UDP, Raw, sendp, BitField, Packet, wrpcap
import csv
width = 100

def create_pkt(ether_dst,ether_type, vlan_id, src_ip, dst_ip):
    pkt = Ether(dst=ether_dst)/Dot1Q(vlan=vlan_id)/IP(src=src_ip, dst=dst_ip)/UDP(dport=1234)/Raw(b'hello')
    return pkt

def create_send_pkt():
    print("\n\n")
    print("="*width)
    print(f"Creating and sending packets".center(width))
    print("="*width)

    with open("./csv_files/flow_entries_8_9_10.csv", mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            interface = f"veth{int(row['port']) * 2}"
            pkt = create_pkt(row["mac"], "0x8100", int(row["vlan"]), row["src_ip"], row["dst_ip"])
            print(f"Interface: {interface:<10} pkt: {pkt.summary()}")
            sendp(pkt, iface=interface, verbose=False)
    print("\n")  