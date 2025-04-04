from scapy.all import Ether, IP, UDP, sendp, Dot1Q
from scapy.all import Packet, BitField
import random
import warnings
import argparse
from time import sleep

# Constants
ETHER_DST = "00:00:00:00:00:01"
ETHER_SRC = "00:00:00:00:00:02"
PAYLOAD = "Hello World"
IPV4_LAYER = IP(src="192.168.233.1", dst="192.168.234.1")
UDP_LAYER = UDP(sport=12345, dport=21)
DEFAULT_PORT = "veth0"

# Custom Telemetry Report Header
class CustomINT(Packet):
    name = "CustomINT"
    fields_desc = [
        BitField("data", 0, 24),
        BitField("ether_type", 0x8100, 16)
    ]

# Suppress specific warnings for missing routes
warnings.filterwarnings("ignore", message="No route found for IPv6 destination")

# Helper Functions
def create_ether_layer(dst=ETHER_DST, src=ETHER_SRC, ether_type=0x8100):
    return Ether(dst=dst, src=src, type=ether_type)

def create_vlan_layer(vlan,vlan_type):
    return Dot1Q(vlan=vlan, type=vlan_type)

def create_custom_int(data=0x123456, ether_type=0x8100):
    return CustomINT(data=data, ether_type=ether_type)

def send_packet(port, *layers):
    pkt = layers[0]
    for layer in layers[1:]:
        pkt /= layer
    pkt.show()
    sendp(pkt, iface=port)

# Case Functions
def case1(port):
    send_packet(port, create_ether_layer(), create_vlan_layer(10,0x800), IPV4_LAYER, UDP_LAYER, PAYLOAD)

def case2(port):
    send_packet(port, create_ether_layer(), create_vlan_layer(random.randint(20, 29), 0x800), IPV4_LAYER, UDP_LAYER, PAYLOAD)

def case3(port):
    send_packet(port, create_ether_layer(ether_type=0x0800), IPV4_LAYER, UDP_LAYER, PAYLOAD)

def case4(port):
    send_packet(port, create_ether_layer(), create_vlan_layer(vlan=40, vlan_type=0x800), IPV4_LAYER, UDP_LAYER, PAYLOAD)

def case5a(port):
    send_packet(port, create_ether_layer(), create_vlan_layer(vlan=50, vlan_type=0x800), IPV4_LAYER, UDP_LAYER, PAYLOAD)

def case5b(port):
    send_packet(port, create_ether_layer(ether_type=0x88a8), create_vlan_layer(vlan=501, vlan_type=0x601), create_custom_int(), create_vlan_layer(vlan=50, vlan_type=0x800), IPV4_LAYER, UDP_LAYER, PAYLOAD)

def case5c(port):
    send_packet(port, create_ether_layer(ether_type=0x88a8), create_vlan_layer(vlan=502, vlan_type=0x601), create_custom_int(ether_type=0x601), create_custom_int(), create_vlan_layer(vlan=50, vlan_type=0x800), IPV4_LAYER, UDP_LAYER, PAYLOAD)

def case6a(port):
    send_packet(port, create_ether_layer(), create_vlan_layer(vlan=60, vlan_type=0x800), IPV4_LAYER, UDP_LAYER, PAYLOAD)

def case6b(port):
    send_packet(port, create_ether_layer(ether_type=0x88a8), create_vlan_layer(vlan=601, vlan_type=0x601), create_custom_int(), create_vlan_layer(vlan=60, vlan_type=0x800), IPV4_LAYER, UDP_LAYER, PAYLOAD)

def case6c(port):
    send_packet(port, create_ether_layer(ether_type=0x88a8), create_vlan_layer(vlan=602, vlan_type=0x601), create_custom_int(ether_type=0x601), create_custom_int(), create_vlan_layer(vlan=60, vlan_type=0x800), IPV4_LAYER, UDP_LAYER, PAYLOAD)

def case7a(port):
    send_packet(port, create_ether_layer(ether_type=0x800), IPV4_LAYER, UDP_LAYER, PAYLOAD)

def case7b(port):
    send_packet(port, create_ether_layer(ether_type=0x88a8), create_vlan_layer(vlan=701, vlan_type=0x601), create_custom_int(ether_type=0x800), IPV4_LAYER, UDP_LAYER, PAYLOAD)

def case7c(port):
    send_packet(port, create_ether_layer(ether_type=0x88a8), create_vlan_layer(vlan=702, vlan_type=0x601), create_custom_int(ether_type=0x601), create_custom_int(ether_type=0x800), IPV4_LAYER, UDP_LAYER, PAYLOAD)

def case8a(port):
    send_packet(port, create_ether_layer(ether_type=0x800), IPV4_LAYER, UDP_LAYER, PAYLOAD)

def case8b(port):
    send_packet(port, create_ether_layer(ether_type=0x88a8), create_vlan_layer(vlan=801, vlan_type=0x601), create_custom_int(ether_type=0x800), IPV4_LAYER, UDP_LAYER, PAYLOAD)

def case8c(port):
    send_packet(port, create_ether_layer(ether_type=0x88a8), create_vlan_layer(vlan=802, vlan_type=0x601), create_custom_int(ether_type=0x601), create_custom_int(ether_type=0x800), IPV4_LAYER, UDP_LAYER, PAYLOAD)


case_functions = {
    ("1", case1,"veth0"),
    ("2", case2,"veth0"),
    ("3", case3,"veth0"),
    ("4", case4,"veth0"),
    ("5a", case5a,"veth0"),
    ("5b", case5b,"veth8"),
    ("5c", case5c,"veth16"),
    ("6a", case6a,"veth0"),
    ("6b", case6b,"veth8"),
    ("6c", case6c,"veth16"),
    ("7a", case7a,"veth2"),
    ("7b", case7b,"veth12"),
    ("7c", case7c,"veth20"),
    ("8a", case8a,"veth4"),
    ("8b", case8b,"veth20"),
    ("8c", case8c,"veth12")
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="P4Runtime test cases")
    parser.add_argument("--case", help="Test case number")
    parser.add_argument("--port", help="Port number", default=DEFAULT_PORT)
    args = parser.parse_args()

    if args.case == "all":
        for case, case_function, port in case_functions:
            case_function(port)
            sleep(2)
    elif args.case:
        for case, case_function, port in case_functions:
            if args.case == case:
                case_function(port)
                break
    else:
        print("Invalid test case number")
        exit(1)
