from scapy.all import Ether, Dot1Q, IP, UDP, Raw, sendp, BitField, Packet, wrpcap

width = 100
ether_addresses = ["00:00:00:00:00:01", "00:00:00:00:00:02", "00:00:00:00:00:03"]

def create_pkt(ether_src):
    ether = Ether(src=ether_src, dst=ether_addresses[1])
    ip = IP(src="192.168.233.5", dst="192.168.233.6")
    udp = UDP(sport=12345, dport=54321)
    payload = "Hello, world! This is a test packet for step 5 and 6."
    pkt = ether / ip / udp / payload

    return pkt

def create_send_pkt(interfaces):
    print("="*width)
    print(f"Creating and sending packets".center(width))
    print("="*width)
    for ether_src in ether_addresses:
        pkt = create_pkt(ether_src)
        for interface in interfaces:
            print(f"Ether Source: {ether_src} | Interface: {interface}")
            sendp(pkt, iface=interface, verbose=False)

    print("\n")
