from scapy.all import Ether, Dot1Q, Dot1AD, IP, UDP, Raw, Packet, BitField, sendp, sniff, sniff, Dot1Q, TCP,bind_layers
import threading
import time
import case_functions.p4_functions as p4f
from scapy.contrib.lldp import LLDPDU


# --- Custom Headers ---
class CustomINT(Packet):
    name = "CustomINT"
    fields_desc = [BitField("data", 0, 32)]

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



def get_pkt_hex_and_binary(pkt,print_hex=False,print_binary=False):
    raw_bytes = bytes(pkt)
    # Hex format: space every byte, group by 16 bytes per line
    hex_str = raw_bytes.hex()
    hex_bytes = [hex_str[i:i+2] for i in range(0, len(hex_str), 2)]
    if print_hex:
        print("Packet in Hex (grouped 16 bytes per line):")
        for i in range(0, len(hex_bytes), 16):
            print(' '.join(hex_bytes[i:i+16]))
    # Binary format: group by 8 bits, break into lines of 4 bytes (32 bits)
    binary_str = ''.join(f'{byte:08b}' for byte in raw_bytes)
    binary_bytes = [binary_str[i:i+8] for i in range(0, len(binary_str), 8)]
    if print_binary:
        print("\nPacket in Binary (grouped by 4 bytes per line):")
        for i in range(0, len(binary_bytes), 4):
            print(' '.join(binary_bytes[i:i+4]))
    return hex_str, binary_str

def get_bin_range(binary_str,start_bit,bit_range=32):
    # print("\nMetadata Type:", binary_str[start_bit:start_bit+bit_range])
    return binary_str[start_bit:start_bit+bit_range]


def print_layer(layer):
    print(f"Layer: {layer.name}")
    layer.remove_payload()
    layer.show()
    
from scapy.all import *

GREY = "\033[90m"
RESET = "\033[0m"  # Reset color after printing

def print_layer_fields(layer, name=None):
    width = 3 * 22
    print(GREY + "_" * width)
    if name:
        print(f"{name}".center(width))
    else:
        print(f"{layer.name}".center(width))
    print("=" * width)
    fields = layer.fields
    field_strings = []

    layer_cp = layer.copy()  # Copy the layer object
    layer_cp.remove_payload()  # Remove the payload from the copy
    # print("HEX: ", layer_cp.__bytes__().hex())
    # print("Length: ", len(layer_cp.__bytes__()))

    
    for k, v in fields.items():
        # Convert "type" fields to hexadecimal if they match known keywords
        if k in ["type"] or k in ["next_hdr"] or k in ["data"] or k in ["proto"]:
            v = f"0x{int(v):04X}"  # Convert to hex format (zero-padded to 4 digits)
        elif k in ["routeid"]: 
            #This is a 128 bit field, print it in hex
            v = f"0x{int(v):032X}"
        elif "tstamp" in k:
            # Convert nanoseconds to seconds
            v_sec = int(v) / 1_000_000_000  
            # Convert to minutes if greater than 3600 seconds
            if v_sec >= 3600:
                v = f"{v_sec / 60:.2f} min"  # Convert to minutes (2 decimal places)
            else:
                v = f"{v_sec:.2f} s"  # Keep it in seconds (2 decimal places)
        field_strings.append(f"{k}={v}")

    # Print every 3 fields per line (handling short last line gracefully)
    for i in range(0, len(field_strings), 3):
        chunk = field_strings[i:i+3]  # Safely slice at most 3 items
        print("|".join(f"{f:{width//3}}" for f in chunk))  


def parse_pkts(pkt, binary_str):
    #Give me the pkt length
    pkt_len = len(pkt)
    # print("Packet Length: ", pkt_len)


    """Parses binary metadata and constructs a Scapy Ether object from the packet."""
    # Extract metadata type from first 8 bits
    md_type = int(binary_str[:8], 2)
    # If metadata type indicates an IngMetadata structure
    if md_type == 0b01111110:
        ig_tstamp = int(binary_str[8:56], 2)  # 48-bit timestamp
        # Construct IngMetadata object and print its fields
        ing_md = IngMetadata(metadata_type=md_type, ig_tstamp=ig_tstamp)
        print_layer_fields(ing_md)
        # Move pointer forward by 8 bytes (64 bits)
        next_hdr_offset = 8
        remaining_data = bytes(pkt)[next_hdr_offset:]
        pkt = Ether(remaining_data)

    # Start with Ether
    ether = pkt.getlayer(Ether)
    print_layer_fields(ether)
    next_hdr = f"0x{ether.type:04X}"
    payload = bytes(pkt.payload)  # move past Ether
    #Print payload size
    pkt_len -= len(payload)
   

    # Dot1AD
    if next_hdr == "0x88A8":
        dot1ad = Dot1AD(payload)
        print_layer_fields(dot1ad)
        next_hdr = f"0x{dot1ad.type:04X}"
        payload = bytes(dot1ad.payload)

    # Polka
    if next_hdr == "0x8842":
        polka = PolkaHdr(payload)
        print_layer_fields(polka)
        next_hdr = f"0x{polka.proto:04X}"
        payload = bytes(polka.payload)

    # Custom INT Shim
    if next_hdr == "0x0601":
        custom_int_shim = CustomINTShim(payload)
        print_layer_fields(custom_int_shim)
        next_hdr = f"0x{custom_int_shim.next_hdr:04X}"
        int_count = custom_int_shim.int_count
        #Print the size left of the received packet
        payload = bytes(custom_int_shim.payload)

        # CustomINT entries
        if len(payload) > 0:
            for i in range(int_count):
                custom_int = CustomINT(payload)
                print_layer_fields(custom_int, f"CustomINT [{i}]")
                payload = bytes(custom_int.payload)

    # VLAN
    if next_hdr == "0x8100":  # VLAN
        dot1q = Dot1Q(payload)
        print_layer_fields(dot1q)
        next_hdr = f"0x{dot1q.type:04X}"
        payload = bytes(dot1q.payload)

    # LLDP
    if next_hdr == "0x88CC":
        lldp = LLDPDU(payload)
        print_layer_fields(lldp)

    # IPv4
    if next_hdr == "0x0800":
        ip = IP(payload)
        print_layer_fields(ip)
        payload = bytes(ip.payload)

        if ip.proto == 17:  # UDP
            udp = UDP(payload)
            print_layer_fields(udp)
            payload = bytes(udp.payload)

        elif ip.proto == 6:  # TCP
            tcp = TCP(payload)
            print_layer_fields(tcp)
            payload = bytes(tcp.payload)

        if payload:
            raw = Raw(payload)
            print_layer_fields(raw)
            #Print the hex of the raw data
            # print("Raw Data: ", raw.load.hex())



    print(RESET)


# --- Packet Printer (for Sniffer) ---
def pkt_hex(pkt,create_pkt=False):
    if create_pkt==False:
        thread_name = threading.current_thread().name
        p4f.print_console("Reset",f"--- Packet Captured on {thread_name.replace('Sniffer-', '')} ---",70)
        # print(f"\n--- Packet Captured on {thread_name.replace('Sniffer-', '')} ---")
    hex_str, binary_str = get_pkt_hex_and_binary(pkt)
    # for i in range(0, len(hex_str),60):
    #     print(''.join(hex_str[i:i+60]), end="\n")
    md_type = get_bin_range(binary_str, 0,8)
    parse_pkts(pkt,binary_str)

    
# --- Background Sniffer (per interface) ---
def sniff_pkts(iface, timeout=5, results_dict=None, lock=None):
    packets = sniff(iface=iface, timeout=timeout, prn=pkt_hex)

    # If packets are captured, update the shared dictionary
    captured = bool(packets)

    if results_dict is not None and lock is not None:
        with lock:  # Ensure thread-safe update
            results_dict[iface] = captured

def start_multi_sniffer_in_background(interfaces, timeout=5):
    threads = []
    results_dict = {}  # Dictionary to store capture results per interface
    lock = threading.Lock()  # Lock for thread-safe operations

    for iface in interfaces:
        sniffer_thread = threading.Thread(
            target=sniff_pkts, 
            args=(iface, timeout, results_dict, lock), 
            daemon=True, 
            name=f"Sniffer-{iface}"
        )
        sniffer_thread.start()
        threads.append(sniffer_thread)

    return threads, results_dict        