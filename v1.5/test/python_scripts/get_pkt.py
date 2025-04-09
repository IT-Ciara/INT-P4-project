import re

def parse_packet(block):
    result = []
    i = 0
    total = len(block)

    # Helper to find next section
    def find_section(name, start=0):
        for j in range(start, total):
            if block[j].startswith(name):
                return j
        return -1

    # Ethernet
    eth_index = find_section("Ethernet")
    if eth_index != -1:
        for line in block[eth_index+2:eth_index+6]:  # skip dashes and header
            if "type=" in line:
                match = re.search(r"type=0x[0-9a-fA-F]+", line)
                if match:
                    eth_type = match.group().split("=")[1]
                    result.append(f"eth({eth_type})")
                break

    # PolkaHdr
    polka_index = find_section("PolkaHdr")
    if polka_index != -1:
        polka_lines = block[polka_index+2:polka_index+6]
        polka_proto = None
        for line in polka_lines:
            if "proto=" in line:
                polka_proto = re.search(r"proto=0x[0-9a-fA-F]+", line)
                polka_proto = polka_proto.group().split("=")[1] if polka_proto else "?"
                break
        if polka_proto:
            result.append(f"polka({polka_proto})")



    # CustomINTShim
    shim_index = find_section("CustomINTShim")
    if shim_index != -1:
        shim_lines = block[shim_index+2:shim_index+7]
        int_count = next_hdr = None
        for line in shim_lines:
            if "int_count=" in line:
                int_count = re.search(r"int_count=\d+", line)
                int_count = int_count.group().split("=")[1] if int_count else "?"
            if "next_hdr=" in line:
                next_hdr = re.search(r"next_hdr=0x[0-9a-fA-F]+", line)
                next_hdr = next_hdr.group().split("=")[1] if next_hdr else "?"
        if int_count and next_hdr:
            result.append(f"int_shim({int_count},{next_hdr})")

    # CustomINT entries
    int_idx = 0
    while True:
        int_label = f"CustomINT [{int_idx}]"
        index = find_section(int_label)
        if index == -1:
            break
        result.append(f"int{int_idx}")
        int_idx += 1

    # First VLAN (o-vlan)
    vlan_indices = [m.start() for m in re.finditer('802.1Q', '\n'.join(block))]
    if len(vlan_indices) >= 1:
        vlan_index = find_section("802.1Q")
        vlan_lines = block[vlan_index+2:vlan_index+6]
        vlan_vid = vlan_type = None
        for line in vlan_lines:
            if "vlan=" in line:
                vlan_vid = re.search(r"vlan=\d+", line)
                vlan_vid = vlan_vid.group().split("=")[1] if vlan_vid else "?"
            if "type=" in line:
                vlan_type = re.search(r"type=0x[0-9a-fA-F]+", line)
                vlan_type = vlan_type.group().split("=")[1] if vlan_type else "?"
        if vlan_vid and vlan_type:
            result.append(f"o-vlan({vlan_vid},{vlan_type})")        

    # Second VLAN (u-vlan)
    if len(vlan_indices) >= 2:
        vlan_index = find_section("802.1Q", start=find_section("CustomINT") + 1)
        vlan_lines = block[vlan_index+2:vlan_index+6]
        vlan_vid = vlan_type = None
        for line in vlan_lines:
            if "vlan=" in line:
                vlan_vid = re.search(r"vlan=\d+", line)
                vlan_vid = vlan_vid.group().split("=")[1] if vlan_vid else "?"
            if "type=" in line:
                vlan_type = re.search(r"type=0x[0-9a-fA-F]+", line)
                vlan_type = vlan_type.group().split("=")[1] if vlan_type else "?"
        if vlan_vid and vlan_type:
            result.append(f"u-vlan({vlan_vid},{vlan_type})")

    lldp_index = find_section("LLDP")
    if lldp_index != -1:
        result.append("lldpdu")

    ipv4_index = find_section("IP")
    if ipv4_index != -1:
        result.append("ipv4")
    
    udp_index = find_section("UDP")
    if udp_index != -1:
        result.append("udp")
    
    tcp_index = find_section("TCP")
    if tcp_index != -1:
        result.append("tcp")


    # Payload
    if find_section("Raw") != -1:
        result.append("payload")

    print("/".join(result))

def iterate_lines_with_context(text):

    import re

    lines = text.strip().splitlines()
    total_lines = len(lines)
    start = False
    no_pkts = False
    i = 0
    block = []
    label = ""
    iface = ""

    while i < total_lines:
        current = lines[i]
        prior = lines[i - 1] if i > 0 else ""
        after = lines[i + 1] if i < total_lines - 1 else ""

        # Detect block start
        if "===" in prior and "===" in after:
            middle_raw = current.strip()
            middle = middle_raw.replace(" ", "").lower()
            if "captured" in middle or "sending" in middle:
                # Process previous block
                if block:
                    print(f"=== {label} Packet ({iface}) ===")
                    parse_packet(block)
                    print()

                block = []
                start = True

                # Determine packet direction and interface
                if "sending" in middle:
                    veth = ''.join(filter(str.isdigit, middle.split("veth")[1]))
                    label = "Input"
                else:
                    veth = ''.join(filter(str.isdigit, middle.split("veth")[1]))
                    label = "Output"

                iface = f"veth{veth}"

                i += 2
                continue

        if start:
            block.append(current.strip())

        i += 1
        # Check for 'NO PACKETS CAPTURED' notice
        if "NO PACKETS CAPTURED ON ANY INTERFACE" in current:
            no_pkts = True
            
    if block and ("capture" in middle or "sending" in middle):
        print(f"=== {label} Packet ({iface}) ===")
        parse_packet(block)
    
    if no_pkts:
        print("=== Output Packet (unknown) ===")
        print("No packets captured\n")



if __name__ == "__main__":
    #Get the data from the txt file
    with open("../python_scripts/pkt_data.txt", "r") as file:
        packet_data = file.read()
    # Run it
    iterate_lines_with_context(packet_data)
