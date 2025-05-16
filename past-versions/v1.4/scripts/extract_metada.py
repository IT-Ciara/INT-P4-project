from scapy.all import sniff, get_if_list

def packet_callback(packet):
    # Get raw packet bytes
    raw_bytes = bytes(packet)

    # Extract the first 4 bytes
    first_4_bytes = raw_bytes[:4]
    
    # Convert to hex
    hex_representation = first_4_bytes.hex()
    
    # Convert to binary (each byte should be 8 bits)
    binary_representation = ' '.join(f'{byte:08b}' for byte in first_4_bytes)

    print(f"\n[+] Captured Packet (First 4 Bytes):")
    print(f"Hex: {hex_representation}")
    print(f"Binary: {binary_representation}")

# List of interfaces to monitor (modify as needed)
interfaces = ['veth0', 'veth2', 'veth4', 'veth6', 'veth8',
              'veth10', 'veth12', 'veth14', 'veth16', 'veth18',
                'veth20', 'veth22', 'veth24', 'veth26', 'veth28', 'veth30']

# Start sniffing on multiple interfaces
print(f"Sniffing on interfaces: {interfaces}... Press Ctrl+C to stop.")
sniff(prn=packet_callback, store=False, iface=interfaces)
