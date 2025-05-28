from scapy.all import Ether, Dot1Q,Dot1AD, IP, UDP, Raw, Packet, BitField, sendp, wrpcap, TCP,bind_layers, sniff
from scapy.contrib.lldp import LLDPDU, LLDPDUChassisID, LLDPDUPortID, LLDPDUTimeToLive, LLDPDUEndOfLLDPDU
from functions.packet_headers import CustomINT, CustomINTShim, PolkaHdr

#=======================================================================================================================
"""
Utility functions for packet creation and parsing in a testing framework.
This module provides functions to create packets based on a given dictionary of packet values,
and to parse packets to extract and print their fields.
This module also includes a function to print the fields of each packet layer in a formatted manner.
"""
#=======================================================================================================================


#=======================================================================================================================
#============================== P A C K E T   B A S E L I N E  =========================================================
#=======================================================================================================================
ethernet = Ether(dst="aa:aa:aa:aa:aa:aa", src="bb:bb:bb:bb:bb:bb", type=0x00800)
s_vlan = Dot1AD(vlan=900,type=0x800)
polka = PolkaHdr(version=1, ttl=64, proto=0x0601, routeid=0x002)
custom_int_shim = CustomINTShim(ig_tstamp=0, stack_full=0, mtu_full=0, padding=0, int_count=1, next_hdr=0x800, reserved=0)
custom_int = CustomINT(data=0x1234)
u_vlan = Dot1Q(vlan=200, type=0x800)
lldp = LLDPDU()/LLDPDUChassisID(subtype=4, id="00:11:22:33:44:55")/LLDPDUPortID(subtype=5, id=str("eth0").encode())/LLDPDUTimeToLive(ttl=120)/LLDPDUEndOfLLDPDU()
ipv4 = IP(src="192.168.230.2", dst="192.168.230.3", proto=17)
udp = UDP(sport=1000, dport=1001)
tcp = TCP(sport=1000, dport=1001)
payload = Raw(load="Hello World")

#===========================================================
#=========== P A C K E T  F U N C T I O N S ================
#===========================================================
GREY = "\033[90m"
RESET = "\033[0m" 

def print_layer_fields(layer, name=None):
    """
    Print the fields of a Scapy layer in a formatted manner.
    :param layer: Scapy layer object.
    :param name: Optional name for the layer, defaults to layer's name.
    """

    width = 3 * 22
    print(GREY + "_" * width)
    print(f"{name or layer.name}".center(width))
    print("=" * width)

    layer_cp = layer.copy()
    layer_cp.remove_payload()

    hex_fields_4 = {"type", "next_hdr", "data", "proto"}
    field_strings = []

    for k, v in layer.fields.items():
        if k in hex_fields_4:
            v = f"0x{int(v):04X}"
        elif k == "routeid":
            v = f"0x{int(v):032X}"
        elif "tstamp" in k:
            v_sec = int(v) / 1_000_000_000
            v = f"{v_sec / 60:.2f} min" if v_sec >= 3600 else f"{v_sec:.2f} s"
        field_strings.append(f"{k}={v}")

    for i in range(0, len(field_strings), 3):
        chunk = field_strings[i:i+3]
        print("|".join(f"{f:{width//3}}" for f in chunk))

def parse_pkts(pkt,print_layers=True):
    """
    Parse a Scapy packet and print its layers and fields in a formatted manner.
    :param pkt: Scapy packet object to parse.
    :param print_layers: Boolean flag to control printing of layer fields.
    :return: A string representation of the parsed packet layers.
    """

    result = []
    pkt_len = len(pkt)

    def extract_and_print(layer_cls, payload, name=None):
        layer = layer_cls(payload)
        if print_layers:
            print_layer_fields(layer, name)
        return layer, bytes(layer.payload)

    # Start with Ether
    ether = pkt.getlayer(Ether)
    if print_layers:
        print_layer_fields(ether)
    next_hdr = f"0x{ether.type:04X}"
    result.append(f"eth({next_hdr})")
    payload = bytes(pkt.payload)
    pkt_len -= len(payload)

    # Dot1AD
    if next_hdr == "0x88A8":
        dot1ad, payload = extract_and_print(Dot1AD, payload)
        next_hdr = f"0x{dot1ad.type:04X}"
        result.append(f"s-vlan({dot1ad.vlan},{next_hdr})")

    # Polka
    if next_hdr == "0x8842":
        polka, payload = extract_and_print(PolkaHdr, payload)
        next_hdr = f"0x{polka.proto:04X}"
        result.append(f"polka({next_hdr})")

    # Custom INT Shim
    if next_hdr == "0x0601":
        shim, payload = extract_and_print(CustomINTShim, payload)
        next_hdr = f"0x{shim.next_hdr:04X}"
        result.append(f"int_shim({shim.int_count},{next_hdr})")

        for i in range(shim.int_count):
            custom_int, payload = extract_and_print(CustomINT, payload, f"CustomINT [{i}]")
            result.append(f"int{i}")

    # VLAN
    if next_hdr == "0x8100":
        dot1q, payload = extract_and_print(Dot1Q, payload)
        next_hdr = f"0x{dot1q.type:04X}"
        result.append(f"u-vlan({dot1q.vlan},{next_hdr})")

    # LLDP
    if next_hdr == "0x88CC":
        lldp, _ = extract_and_print(LLDPDU, payload)
        result.append("lldp")

    # LCTP
    elif next_hdr == "0x8809":
        raw = Raw("This is a LCTP payload")
        if print_layers:
            print_layer_fields(raw)
        result.append("lctp")

    # IPv4 and transport
    elif next_hdr == "0x0800":
        ip, payload = extract_and_print(IP, payload)
        result.append("ipv4")

        if ip.proto == 17:  # UDP
            udp, payload = extract_and_print(UDP, payload)
            result.append("udp")
        elif ip.proto == 6:  # TCP
            tcp, payload = extract_and_print(TCP, payload)
            result.append("tcp")

        if payload:
            raw = Raw(payload)
            if print_layers:
                print_layer_fields(raw)
            result.append("payload")

    print(RESET)
    if print_layers:
        print("/".join(result))
    return "/".join(result)

def create_pkts(df_pkts):
    """
    Create a Scapy packet based on the provided DataFrame of packet values.
    :param df_pkts: DataFrame containing packet values.
    :return: Scapy packet object.
    """
    
    pkt = None
    # print(df_pkts['Input pkt'])
    input_pkt = df_pkts['Input pkt'].split('/')
    df_pkts.pop('Input pkt')  # Remove the key directly from the dict
    i = 0
    while i < len(input_pkt):
        layer = input_pkt[i]
        if layer.startswith('eth'):
            ethernet.type=int(layer.split('(')[1].split(')')[0], 16)
            ethernet.src=df_pkts['hdr.ethernet.src_addr']
            ethernet.dst=df_pkts['hdr.ethernet.dst_addr']
            pkt = ethernet
        elif layer.startswith('lldp'):
            pkt /= lldp
        elif layer.startswith('lctp'):
            payload.load="lctp"
        elif layer.startswith('s-vlan'):
            s_vlan.vlan=int(layer.split('(')[1].split(',')[0])
            s_vlan.type=int(layer.split(',')[1].split(')')[0], 16)
            pkt /= s_vlan
        elif layer.startswith('polka'):
            polka.proto=int(layer.split('(')[1].split(')')[0], 16)
            pkt /= polka
        elif layer.startswith('int_shim'):
            custom_int_shim.int_count=int(layer.split('(')[1].split(',')[0])
            custom_int_shim.next_hdr=int(layer.split(',')[1].split(')')[0], 16)
            pkt /= custom_int_shim
            for j in range(0, custom_int_shim.int_count):
                custom_int.data=int(j+1)
                pkt /= custom_int
        elif layer.startswith('u-vlan'):
            u_vlan.vlan=int(layer.split('(')[1].split(',')[0])
            u_vlan.type=int(layer.split(',')[1].split(')')[0], 16)
            pkt /= u_vlan
        elif layer.startswith('ipv4'):
            ipv4.src=df_pkts['hdr.ipv4.src_addr']
            ipv4.dst=df_pkts['hdr.ipv4.dst_addr']
            #Check what's the next layer 
            proto = input_pkt[i+1]
            if proto.startswith('udp'):
                ipv4.proto=17
            elif proto.startswith('tcp'):
                ipv4.proto=6
            pkt /= ipv4
        elif layer.startswith('udp'):
            pkt /= udp
        elif layer.startswith('tcp'):
            pkt /= tcp
        elif layer.startswith('payload'):
            pkt /= payload
        i += 1
    # parse_pkts(pkt)
    return pkt