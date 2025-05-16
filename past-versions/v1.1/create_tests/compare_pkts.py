from scapy.all import rdpcap, hexdump, Ether, IP, UDP, Raw, Dot1Q, IPv6, TCP, Packet, BitField
import struct
import hashlib

layers = ["ethernet", "vlan_0x8100_0", "custom_int1", "custom_int2", "custom_int3", "custom_int4", "custom_int5", "vlan_0x88a8_0", "ipv4", "ipv6", "udp", "tcp", "payload"]

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





def compare_pkts(pkt1, pkt2, counter):
    same_layers = []
    different_layers = []
    missing_layers = []

    print("Comparing packets")
    for layer in layers:
        # print(f"\nLayer: {layer}")
        layer_data1 = pkt1[layer]
        layer_data2 = pkt2[layer]

        if layer_data1 is None or layer_data2 is None or layer_data1 == [] or layer_data2 == []:
            # Handle missing layers
            missing_layers.append(layer)
            # print(f"One or both packets lack layer {layer}")
        else:
            try:
                # Handle lists of layers (e.g., custom_int_layers)
                if isinstance(layer_data1, list) and isinstance(layer_data2, list):
                    differences_found = False
                    for i, (item1, item2) in enumerate(zip(layer_data1, layer_data2)):
                        item_bytes1 = bytes(item1) if hasattr(item1, "build") else item1.build()
                        item_bytes2 = bytes(item2) if hasattr(item2, "build") else item2.build()
                        hash1 = calculate_hash(item_bytes1)
                        hash2 = calculate_hash(item_bytes2)

                        if hash1 != hash2:
                            differences_found = True
                            print(f"Difference in {layer} - Item {i + 1}:")
                            print(f"Packet {counter}: {item1}")
                            print(f"Packet {counter+1}: {item2}")
                            print(f"Hash 1: {hash1}")
                            print(f"Hash 2: {hash2}")

                        counter+=2
                        
                    if not differences_found:
                        same_layers.append(layer)
                else:
                    # Compare single layers
                    layer_bytes1 = bytes(layer_data1) if hasattr(layer_data1, "build") else layer_data1.build()
                    layer_bytes2 = bytes(layer_data2) if hasattr(layer_data2, "build") else layer_data2.build()
                    hash1 = calculate_hash(layer_bytes1)
                    hash2 = calculate_hash(layer_bytes2)

                    if hash1 == hash2:
                        same_layers.append(layer)
                    else:
                        different_layers.append(layer)
                        print(f"Difference in {layer}:")
                        print(f"Packet {counter}: {layer_data1}")
                        print(f"Packet {counter+1}: {layer_data2}")
                        print(f"Hash 1: {hash1}")
                        print(f"Hash 2: {hash2}")
                        counter+=2
            except Exception as e:
                print(f"Error processing layer {layer}: {e}")
                different_layers.append(layer)

    # Summary of results
    print("\nComparison Summary:")
    print(f"Same layers: {same_layers}")
    print(f"Different layers: {different_layers}\n\n")
    # print(f"Missing layers: {missing_layers}")
    return counter

def compare_packets(i):
    pcaps_path = "./wireshark/"
    packets = rdpcap(f"{pcaps_path}case{i}.pcap")
    packets = sorted(packets, key=lambda pkt: pkt.time)

    # Group packets in pairs of 2
    print(f"Total packets: {len(packets)}")

    counter = 1
    for pkt1, pkt2 in zip(packets[::2], packets[1::2]):
        print("\n#*-------------------------------------------------------------------------------------------------------------------------------*")
        # Process the grouped packets
        # print(f"Pair: ({pkt1.summary()}\n{pkt2.summary()})")
        packet_data_1 = parse_packet(pkt1)
        packet_data_2 = parse_packet(pkt2)
        # Print or process packet data for each pair
        counter = compare_pkts(packet_data_1, packet_data_2, counter)

compare_packets(8)
        
