from scapy.all import Ether, Dot1Q,Dot1AD, IP, UDP, Raw, Packet, BitField, sendp, wrpcap, TCP,bind_layers, sniff
from scapy.contrib.lldp import LLDPDU, LLDPDUChassisID, LLDPDUPortID, LLDPDUTimeToLive, LLDPDUEndOfLLDPDU

#=======================================================================================================================
#============================== P A C K E T   H E A D E R S ============================================================
#=======================================================================================================================

# Custom Telemetry Report Header
class CustomINT(Packet):
    name = "CustomINT"
    fields_desc = [
        BitField("data", 0X1234, 32),
    ]
class CustomINTShim(Packet):
    name = "CustomINTShim"
    fields_desc = [
        BitField("ig_tstamp", 0, 48),
        BitField("stack_full", 0, 1),
        BitField("mtu_full", 0, 1),
        BitField("padding", 0, 6),
        BitField("int_count", 1, 8),
        BitField("next_hdr", 0x0601, 16),
        BitField("reserved", 0, 16)
    ]
class IngMetadata(Packet):
    name = "IngMetadata"
    fields_desc = [
        BitField("metadata_type", 0, 8),
        BitField("ig_tstamp", 0, 48),
    ]    
class PolkaHdr(Packet):
    name = "PolkaHdr"
    fields_desc = [
        BitField("version", 1, 8),
        BitField("ttl", 64, 8),
        BitField("proto", 0x800, 16),
        BitField("routeid", 0x002,128)
    ]

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