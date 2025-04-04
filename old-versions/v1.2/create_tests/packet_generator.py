from scapy.all import Ether, Dot1Q, IP, UDP, Raw, sendp, BitField, Packet

# Custom Telemetry Report Header
class CustomINT(Packet):
    name = "CustomINT"
    fields_desc = [
        BitField("data", 0, 32),
    ]

class CustomINTShim(Packet):
    name = "CustomINTShim"
    fields_desc = [
        BitField("int_count", 0, 8),
        BitField("next_hdr", 0x8100, 16)
    ]

int_data = int('1234', 16)  # Convert the hexadecimal string to an integer


def create_pkt_payload():
    return Raw(load="This is the payload data")


def convert_to_string(pkt):
    #convert the array to string
    pkt_str = ""
    for i in pkt:
        pkt_str += str(i) + "/"
    return pkt_str



def create_packet(pkt, port):
    packet_str = convert_to_string(pkt)
    print("*-------------------*")
    print("PORT")
    veth_port = f"veth{port*2}"
    print("Veth port:", veth_port)
    print("*-------------------*")
    print("Input Packet String:", packet_str)
    print("*-------------------*")
    # Split the packet string into layers
    layers = packet_str.split('/')
    # Initialize with the Ethernet layer
    try:
        if layers[0].startswith("eth(") and layers[0].endswith(")"):
            ether_type = int(layers[0][4:-1], 16)  # Extract EtherType
        else:
            raise ValueError("Invalid Ethernet header format")
    except Exception as e:
        print(f"Error parsing EtherType: {e}")
        return
    pkt = Ether(type=ether_type, dst="00:00:00:00:00:01", src="00:00:00:00:00:02")
    # Process subsequent layers
    for layer in layers[1:]:
        if layer.startswith("u-vlan(") and layer.endswith(")"):
            vlan_info = layer[7:-1].split(',')
            vlan_id = int(vlan_info[0])  # VLAN ID
            vlan_type = int(vlan_info[1], 16)
            pkt /= Dot1Q(vlan=vlan_id, type=vlan_type)
        elif layer.startswith("IPv4"):
            pkt /= IP(src="192.168.233.1", dst="192.168.234.1")
        elif layer.startswith("UDP"):
            pkt /= UDP(sport=12345, dport=3000)
        elif layer.startswith("Payload"):
            pkt /= create_pkt_payload()
        elif layer.startswith("s-vlan(") and layer.endswith(")"):
            vlan_info = layer[7:-1].split(',')
            vlan_id = int(vlan_info[0])
            vlan_type = int(vlan_info[1], 16)
            pkt /= Dot1Q(vlan=vlan_id, type=vlan_type)
        elif layer.startswith("int_shim") and layer.endswith(")"):
            shim_info = layer[9:-1].split(',')
            int_count = int(shim_info[0])
            next_hdr = int(shim_info[1], 16)  # Corrected to keep it as an integer
            pkt /= CustomINTShim(int_count=int_count, next_hdr=next_hdr)
        elif layer.startswith("int"):
            pkt /= CustomINT(data=int_data)
    # Show packet details
    # Uncomment the line below to send the packet
    sendp(pkt, iface=veth_port)
    