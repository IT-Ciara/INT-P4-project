from scapy.all import rdpcap, hexdump, Ether, IP, UDP, Raw, Dot1Q, IPv6, TCP, Packet, BitField
import struct
import hashlib


# Custom Telemetry Report Header
class CustomINT(Packet):
    name = "CustomINT"
    fields_desc = [
        BitField("data", 0, 24),
        BitField("ether_type", 0x8100, 16)
    ]

def calculate_hash(data):
    """Calculate SHA-256 hash of data."""
    return hashlib.sha256(data).hexdigest()

# Define a function to parse bytes into specific layers based on offset
def parse_packet(pkt):
    # Dictionary to store parsed data for a single packet
    packet_data = {
        "ethernet": None,
        "vlan_0x8100_0": None,
        "custom_int1": None,
        "custom_int2": None,
        "custom_int3": None,
        "custom_int4": None,
        "custom_int5": None,
        "vlan_0x88a8_0": None,
        "ipv4": None,
        "ipv6": None,
        "udp": None,
        "tcp": None,
        "payload": None
    }

    # Extract Ethernet header (first 14 bytes)
    eth_bytes = bytes(pkt)[:14]
    eth_layer = Ether(eth_bytes)
    packet_data["ethernet"] = eth_layer

    offset = 14  # Start offset for the next layer
    if eth_layer.type == 0x8100:
        parse_vlan_layer(pkt, offset, packet_data)
    elif eth_layer.type == 0x88a8:
        parse_qinq_vlan_layer(pkt, offset, packet_data)
    elif eth_layer.type == 0x0800:
        parse_ip_layer(pkt, offset, packet_data)
    elif eth_layer.type == 0x86dd:
        parse_ipv6_layer(pkt, offset, packet_data)
    
    return packet_data

def parse_ipv6_layer(pkt, offset, packet_data):
    ipv6_bytes = bytes(pkt)[offset:offset+40]
    ipv6_layer = IPv6(ipv6_bytes)
    packet_data["ipv6"] = ipv6_layer

    offset += 40
    if ipv6_layer.nh == 17:  # UDP protocol
        parse_udp_layer(pkt, offset, packet_data)
    elif ipv6_layer.nh == 6:  # TCP protocol
        parse_tcp_layer(pkt, offset, packet_data)

def parse_vlan_layer(pkt, offset, packet_data):
    vlan_bytes = bytes(pkt)[offset:offset+4]
    vlan_layer = Dot1Q(vlan_bytes)
    packet_data["vlan_0x8100_0"] = vlan_layer

    offset += 4
    if vlan_layer.type == 0x0800:
        parse_ip_layer(pkt, offset, packet_data)
    elif vlan_layer.type == 0x0601:
        parse_custom_int_layer(pkt, offset, packet_data)
    elif vlan_layer.type == 0x8100:
        parse_vlan_layer(pkt, offset, packet_data)
    elif vlan_layer.type == 0x86dd:
        parse_ipv6_layer(pkt, offset, packet_data)

def parse_qinq_vlan_layer(pkt, offset, packet_data):
    qinq_bytes = bytes(pkt)[offset:offset+4]
    qinq_layer = Dot1Q(qinq_bytes)
    packet_data["vlan_0x88a8_0"] = qinq_layer

    offset += 4
    if qinq_layer.type == 0x0601:
        parse_custom_int_layer(pkt, offset, packet_data)
    elif qinq_layer.type == 0x8100:
        parse_vlan_layer(pkt, offset, packet_data)
    elif qinq_layer.type == 0x0800:
        parse_ip_layer(pkt, offset, packet_data)
    elif qinq_layer.type == 0x86dd:
        parse_ipv6_layer(pkt, offset, packet_data)

def parse_custom_int_layer(pkt, offset, packet_data, int_count=1):
    custom_int_bytes = bytes(pkt)[offset:offset+5]
    custom_int = CustomINT(custom_int_bytes)
    packet_data[f"custom_int{int_count}"] = custom_int

    offset += 5
    if custom_int.ether_type == 0x8100:
        parse_vlan_layer(pkt, offset, packet_data)
    elif custom_int.ether_type == 0x0800:
        parse_ip_layer(pkt, offset, packet_data)
    elif custom_int.ether_type == 0x0601:
        parse_custom_int_layer(pkt, offset, packet_data, int_count + 1)

def parse_ip_layer(pkt, offset, packet_data):
    ip_bytes = bytes(pkt)[offset:offset+20]
    ip_layer = IP(ip_bytes)
    packet_data["ipv4"] = ip_layer

    offset += 20
    if ip_layer.proto == 17:  # UDP protocol
        parse_udp_layer(pkt, offset, packet_data)

def parse_udp_layer(pkt, offset, packet_data):
    udp_bytes = bytes(pkt)[offset:offset+8]
    udp_layer = UDP(udp_bytes)
    packet_data["udp"] = udp_layer

    payload_offset = offset + 8
    if payload_offset < len(pkt):
        parse_raw_payload(pkt, payload_offset, packet_data)

def parse_tcp_layer(pkt, offset, packet_data):
    tcp_bytes = bytes(pkt)[offset:offset+20]
    tcp_layer = TCP(tcp_bytes)
    packet_data["tcp"] = tcp_layer

    payload_offset = offset + 20
    if payload_offset < len(pkt):
        parse_raw_payload(pkt, payload_offset, packet_data)

def parse_raw_payload(pkt, offset, packet_data):
    raw_data = bytes(pkt)[offset:]
    payload_layer = Raw(raw_data)
    packet_data["payload"] = payload_layer


# Function to determine if two layers match, skipping if both are None
def layer_match(layer_data1, layer_data2, layer,print_b=True):
    if not layer_data1 and not layer_data2:
        return "skip"
    print(f"\nLAYER {layer.upper()}")    
    # Convert the show() output to a string or "None" if the layer data is missing
    data1 = layer_data1.show(dump=True) if layer_data1 else "None"
    data2 = layer_data2.show(dump=True) if layer_data2 else "None"

    # Split the show output lines to display them side by side
    data1_lines = data1.splitlines()
    data2_lines = data2.splitlines()
    max_len = max(len(data1_lines), len(data2_lines))

    # Print side-by-side with alignment, even if one side is None
    if print_b:
        print(f"{'Layer Data 1':<50} {'Layer Data 2':<50}")
        print("=" * 100)
        for i in range(max_len):
            line1 = data1_lines[i] if i < len(data1_lines) else ""
            line2 = data2_lines[i] if i < len(data2_lines) else ""
            print(f"{line1:<50} {line2:<50}")
    
    # Convert both layers to byte-compatible formats for hashing and comparison
    data1_bytes = str(layer_data1).encode() if layer_data1 else b""
    data2_bytes = str(layer_data2).encode() if layer_data2 else b""
    
    # Compare hash values and return result
    return calculate_hash(data1_bytes) == calculate_hash(data2_bytes)


def compare_packets(case, pkts, index):
    # Load packets from pcap file
    packets = rdpcap(f"./wireshark/case{case}.pcap")
    packets = sorted(packets, key=lambda pkt: pkt.time)
    # Parse each packet and store in a list
    parsed_packets = [parse_packet(pkt) for pkt in packets]
    
    # Compare each packet and print match results layer by layer, skipping empty layers
    for i in range(0, len(parsed_packets) - 1, 2):
        print(f"Packet {i + 1} Details:", pkts[index][0])
        print(f"Packet {i + 2} Details:", pkts[index][1])
        print(f"\n\nComparing Packet {i + 1} with Packet {i + 2}")
        
        pkt1 = packets[i]
        pkt2 = packets[i + 1]
        
        # Calculate and compare hash of the entire packet bytes
        pkt1_hash = calculate_hash(bytes(pkt1))
        pkt2_hash = calculate_hash(bytes(pkt2))
        
        if pkt1_hash == pkt2_hash:
            print("Complete Packet Hash: Yes, match")
        else:
            print("Complete Packet Hash: No, mismatch")
        
        # Layer-by-layer comparison
        pkt1_data = parsed_packets[i]
        pkt2_data = parsed_packets[i + 1]
        
        # Track if all layers match for a final comparison result
        all_layers_match = True
        
        # Compare layers
        for layer in pkt1_data.keys():
            pkt1_layer_data = pkt1_data[layer]
            pkt2_layer_data = pkt2_data[layer]
            
            # Check if layers match or if both are None (skip)
            match_result = layer_match(pkt1_layer_data, pkt2_layer_data, layer,print_b=True)
            if match_result == "skip":
                continue  # Skip the layer comparison if both layers are None
            elif match_result:
                print(f"{layer}: Yes, match")
            else:
                print(f"{layer}: No, mismatch")
                all_layers_match = False  # Set flag to False if any layer does not match
        
        # Final result for packet comparison
        if all_layers_match:
            print(f"\nResult: Packet {i + 1} and Packet {i + 2} are identical in all layers.\n\n")
        else:
            print(f"\nResult: Packet {i + 1} and Packet {i + 2} have differences.\n\n")
        
        index += 1
    return index
