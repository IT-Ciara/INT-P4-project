from scapy.all import Ether, Dot1Q, IP, UDP, Raw, sendp, raw
import hashlib

def calculate_hash(data):
    """Calculate SHA-256 hash of data."""
    return hashlib.sha256(data).hexdigest()

def create_packet(ingress_pkt_incoming, port):
    print("*-------------------*")
    print("PORT")
    veth_port = f"veth{port*2}"
    print("Veth port:", veth_port)
    print("*-------------------*")
    print(ingress_pkt_incoming)
    print("*-------------------*")

    # Initialize with the Ethernet layer
    ether_type = int(ingress_pkt_incoming[0][4:-1], 16)  # Extract and convert EtherType
    pkt = Ether(type=ether_type, dst="00:00:00:00:00:01", src="00:00:00:00:00:02")

    # Check and add VLAN layers if present
    for layer in ingress_pkt_incoming[1:]:
        if "u-vlan" in layer or "c-vlan" in layer:
            vlan_info = layer[layer.index('(')+1:-1].split(',')
            vlan_id = int(vlan_info[0])
            vlan_type = int(vlan_info[1], 16)  # Usually 0x800 for IPv4 packets

            # Add Dot1Q layer for VLAN tagging
            pkt /= Dot1Q(vlan=vlan_id, type=vlan_type)
            
        elif layer == "IPv4":
            pkt /= IP(src="192.168.233.1", dst="192.168.234.1")
            

        elif layer == "UDP":
            pkt /= UDP(sport=12345, dport=3000)
            
        elif layer == "Payload":
            pkt /= Raw(load="This is the payload data")  # Adjust payload as needed
            
    # Show packet details
    print("Final crafted packet:")
    # print(pkt.summary())
    print("Packet details:")
    pkt.show()


    # Send the packet on the specified interface
    sendp(pkt, iface=veth_port)


