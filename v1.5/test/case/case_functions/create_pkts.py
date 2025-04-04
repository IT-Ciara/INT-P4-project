from scapy.all import Ether, Dot1Q,Dot1AD, IP, UDP, Raw, Packet, BitField, sendp, wrpcap, TCP,bind_layers
from scapy.contrib.lldp import LLDPDU, LLDPDUChassisID, LLDPDUPortID, LLDPDUTimeToLive, LLDPDUEndOfLLDPDU
import copy
from case_functions.sniff_pkts import print_layer, parse_pkts,pkt_hex



# Custom Telemetry Report Header
class CustomINT(Packet):
    name = "CustomINT"
    fields_desc = [
        BitField("data", 0, 32),
    ]

class CustomINTShim(Packet):
    name = "CustomINTShim"
    fields_desc = [
        BitField("ig_tstamp", 0, 48),
        BitField("stack_full", 0, 1),
        BitField("mtu_full", 0, 1),
        BitField("padding", 0, 6),
        BitField("int_count", 0, 8),
        BitField("next_hdr", 0, 16),
        BitField("reserved", 0, 16)
    ]

class IngMetadata(Packet):
    name = "IngMetadata"
    fields_desc = [
        BitField("metadata_type", 0, 8),
        BitField("ig_tstamp", 0, 48),
        # BitField("rm_s_vlan", 0, 1),
        # BitField("add_int", 0, 1),
        # BitField("reserved", 0, 6)
    ]    


class PolkaHdr(Packet):
    name = "PolkaHdr"
    fields_desc = [
        BitField("version", 0, 8),
        BitField("ttl", 0, 8),
        BitField("proto", 0, 16),
        BitField("routeid", 0,128)
    ]


# Layer binding definitions for custom protocol dissection

# Bind custom metadata to start before Ethernet
bind_layers(IngMetadata, Ether)

# Bind standard and custom layers to Ether
bind_layers(Ether, Dot1Q, type=0x88A8)               # VLAN stacking (802.1ad / QinQ)
bind_layers(Ether, CustomINTShim, type=0x0601)       # Custom INT Shim directly on Ether
bind_layers(Ether, PolkaHdr, type=0x8842)            # Polka header after Ether


# Bind layers following PolkaHdr
bind_layers(PolkaHdr, CustomINTShim, proto=0x0601)   # Custom INT Shim after Polka

# Bind Dot1AD (QinQ) to Custom INT Shim if it follows
bind_layers(Dot1AD, CustomINTShim, type=0x0601)

# Chain INT Shim to INT metadata and then to VLAN
bind_layers(CustomINTShim, CustomINT)
bind_layers(CustomINT, Dot1Q)
bind_layers(CustomINT, IP)


# Default configuration
default_config = {
    "ethernet": {
        "valid": True,
        "dst_addr": "aa:aa:aa:aa:aa:aa",
        "src_addr": "bb:bb:bb:bb:bb:bb",
        "ether_type": 0x8100
    },
    "polka":{
        "valid":False,
        "version": 1,
        "ttl": 64,
        "proto": 0x800,
        "routeid": 0x0
    },
    "outer_vlan": {
        "valid": True,
        "vid": 100,
        "ether_type": 0x800
    },
    "custom_int_shim": {
        "valid": False,
        "ig_tstamp": 0,
        "stack_full": 0,
        "mtu_full": 0,
        "padding": 0,
        "int_count": 0,
        "next_hdr": 0,
        "reserved": 0
    },
    "inner_vlan": {
        "valid": False,
        "vid": 0,
        "ether_type": 0
    },
    "ipv4": {
        "valid": True,
        "src_addr": "192.168.230.2",
        "dst_addr": "192.168.230.3",
        "protocol": 17
    },
    "udp": {
        "valid": True,
        "src_port": 1000,
        "dst_port": 1001
    },
    "tcp": {
        "valid": False,
        "src_port": 1000,
        "dst_port": 1001
    },
    "raw": {
        "valid": True,
        "data": "Packet Payload Here"
    },
    "lldp": {
        "valid": False,
        "chassis_id": "00:11:22:33:44:55",
        "port_id": "eth0",
        "ttl": 120
    }

}

GREY = "\033[90m"
RESET = "\033[0m"  # Reset color after printing

def print_all_layers(layer):
    width = 3 * 22
    print(GREY + "_" * width)
    print(f"{layer.name}".center(width))
    print("=" * width)
    if layer is None:
        print("Layer not present" + RESET)
        return
    
    fields = layer.fields
    field_strings = []
    
    for k, v in fields.items():
        # Convert "type" fields to hexadecimal if they match known keywords
        if k in ["type"]:  # Add other field names if needed
            v = f"0x{int(v):04X}"  # Convert to hex format (zero-padded to 4 digits)
        field_strings.append(f"{k}={v}")

    # Print every 3 fields per line (handling short last line gracefully)
    for i in range(0, len(field_strings), 3):
        chunk = field_strings[i:i+3]  # Safely slice at most 3 items
        print("|".join(f"{f:{width//3}}" for f in chunk) + RESET)  # Adjust spacing if needed

def get_specific_field_from_config(header, field):
    return default_config[header][field]

# Merge user overrides into defaults
def load_config(user_config=None):
    config = copy.deepcopy(default_config)
    if user_config:
        for key, value in user_config.items():
            if key in config and isinstance(value, dict):
                config[key].update(value)
            else:
                config[key] = value
    return config

# Build the packet dynamically based on config
def build_pkt(config):
    next_hdr = ""
    pkt = Ether(dst=config["ethernet"]["dst_addr"],
                src=config["ethernet"]["src_addr"],
                type=config["ethernet"]["ether_type"]) if config["ethernet"]["valid"] else Ether()
    next_hdr = config["ethernet"]["ether_type"]

    if config["polka"]["valid"] and next_hdr == 0x8842:
        pkt /= PolkaHdr(
            version=config["polka"]["version"],
            ttl=config["polka"]["ttl"],
            proto=config["polka"]["proto"],
            routeid=config["polka"]["routeid"]
        )
        next_hdr = config["polka"]["proto"]
    if config["custom_int_shim"]["valid"] and next_hdr == 0x0601:
        pkt /= CustomINTShim(
            ig_tstamp=config["custom_int_shim"]["ig_tstamp"],
            stack_full=config["custom_int_shim"]["stack_full"],
            mtu_full=config["custom_int_shim"]["mtu_full"],
            padding=config["custom_int_shim"]["padding"],
            int_count=config["custom_int_shim"]["int_count"],
            next_hdr=config["custom_int_shim"]["next_hdr"],
            reserved=config["custom_int_shim"]["reserved"]
        )
        next_hdr = config["custom_int_shim"]["next_hdr"]
        if config["custom_int_shim"]["int_count"] > 0:
            value = 0x123
            for i in range(config["custom_int_shim"]["int_count"]):
                pkt /= CustomINT(data=value)
                value += 30

    if config["outer_vlan"]["valid"] and next_hdr == 0x8100:
        pkt /= Dot1Q(vlan=config["outer_vlan"]["vid"], type=config["outer_vlan"]["ether_type"])
        next_hdr = config["outer_vlan"]["ether_type"]
    if next_hdr == 0x88A8:
        pkt /= Dot1AD(vlan=config["outer_vlan"]["vid"], type=config["outer_vlan"]["ether_type"])
        next_hdr = config["outer_vlan"]["ether_type"]

    if config["lldp"]["valid"] and config["ethernet"]["ether_type"] == 0x88cc:
        pkt /=  LLDPDU() / \
                LLDPDUChassisID(subtype=4, id=config["lldp"]["chassis_id"]) / \
                LLDPDUPortID(subtype=5, id=str(config["lldp"]["port_id"]).encode())  / \
                LLDPDUTimeToLive(ttl=config["lldp"]["ttl"]) / \
                LLDPDUEndOfLLDPDU()
        
    if config["inner_vlan"]["valid"]:
        pkt /= Dot1Q(vlan=config["inner_vlan"]["vid"], type=config["inner_vlan"]["ether_type"])
    if config["ipv4"]["valid"]:
        pkt /= IP(src=config["ipv4"]["src_addr"],
                  dst=config["ipv4"]["dst_addr"],
                  proto=config["ipv4"]["protocol"])
    if config["udp"]["valid"]:
        pkt /= UDP(sport=config["udp"]["src_port"], dport=config["udp"]["dst_port"])
    if config["tcp"]["valid"]:
        pkt /= TCP(sport=config["tcp"]["src_port"], dport=config["tcp"]["dst_port"])
    if config["raw"]["valid"]:
        pkt /= Raw(load=config["raw"]["data"])
    return pkt

def print_layer(layer):
    print(f"Layer: {layer.name}")
    layer.remove_payload()
    layer.show()

# Example user override - user can modify anything they want
user_overrides = {
    # "ethernet": {"src_addr": "00:00:00:11:22:33"},
    # "ipv4": {"src_addr": "10.0.0.1", "dst_addr": "10.0.0.2"},
    # "udp": {"dst_port": 1234},
    # "raw": {"data": "TelemetryPayload"}
}

def send_pkts(user_overrides=user_overrides,show_layer=None,interface=0):
    # Load final config (defaults + overrides)
    final_config = load_config(user_overrides)
    # Build the packet
    pkt = build_pkt(final_config)
    pkt_copy = pkt.copy()
    pkt_hex(pkt_copy,create_pkt=True)

    # if show_layer:
        
    #     for layer in show_layer:
    #         if layer.lower() == "ether":
    #             print("Ether")
    #             l = pkt_copy.copy().getlayer(Ether)
    #             print_layer(l)
    #         elif layer.lower() == "ip":
    #             l = pkt_copy.copy().getlayer(IP)
    #             print_layer(l)
    #         elif layer.lower() == "udp" and UDP in pkt:
    #             l = pkt_copy.copy().getlayer(UDP)
    #             print_layer(l)
    #         elif layer.lower() == "tcp" and TCP in pkt:
    #             l = pkt_copy.copy().getlayer(TCP)
    #             print_layer(l)
    #         elif layer.lower() == "dot1q":
    #             l = pkt_copy.copy().getlayer(Dot1Q)
    #             print_layer(l)
    # else:
    #     layers = pkt_copy.layers()
    #     for layer in layers:
    #         print_all_layers(pkt_copy.getlayer(layer))
        

    # Send the packet
    sendp(pkt, iface=f"veth{interface*2}", verbose=False)


# Optional - send or write to pcap
# sendp(packet, iface="eth0")
# wrpcap("packet.pcap", packet)


if __name__ == "__main__":
    send_pkts(user_overrides,show_layer=["ether"])