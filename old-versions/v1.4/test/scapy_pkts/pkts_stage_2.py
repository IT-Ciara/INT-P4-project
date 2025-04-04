from scapy.all import Ether, Dot1Q, IP, UDP, Raw, sendp, BitField, Packet, wrpcap
MAX = 1
import random
width = 100
def create_send_pkt(interfaces):
    print("\n\n")
    print("="*width)
    print(f"Creating and sending packets".center(width))
    print("="*width)
    numbers = []
    ether = Ether(src="11:11:11:11:11:11", dst="22:22:22:22:22:22")
    ip = IP(src="192.168.233.5", dst="192.168.233.6")
    udp = UDP(sport=12345, dport=54321)
    payload = "Hello, world! This is a test packet for stage 2"
    pkt = ether / ip / udp / payload
    for interface in interfaces:
        number_of_packets = random.randint(1, MAX)
        print(f"Interface: {interface:<10}| Number of packets: {number_of_packets:<5}")
        numbers.append([interface, number_of_packets])
        for i in range(0, number_of_packets):
            sendp(pkt, iface=interface,inter=0.00001,verbose=False)
    print("\n")
    return numbers