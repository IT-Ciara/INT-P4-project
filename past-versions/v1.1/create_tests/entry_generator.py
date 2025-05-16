import os

# Set to track existing entries and avoid duplicates
existing_entries = set()

# ---------------------------------------------------------------------------------------------------
# VLAN Action Definitions
# ---------------------------------------------------------------------------------------------------
INGRESS_VLAN_ACTIONS = ['forward', 'swap_vlan_id', 'swap_vlan', 'pop_outer_vlan']
INGRESS_NORMAL_ACTIONS = ['push_outer_vlan']
EGRESS_VLAN_ACTIONS = ['shift_int', 'push_int', 'pop_and_vlan', 'nothing']
EGRESS_NORMAL_ACTIONS = ['pop_int', 'pop_int_and_add_vlan']

# ---------------------------------------------------------------------------------------------------
# Traffic Table Names
# ---------------------------------------------------------------------------------------------------
INGRESS_VLAN_TRAFFIC_TABLE = "p4.Ingress.ingress_vlan_traffic_table"
INGRESS_NORMAL_TRAFFIC_TABLE = "p4.Ingress.ingress_normal_traffic_table"
EGRESS_VLAN_TRAFFIC_TABLE = "p4.Egress.egress_vlan_traffic_table"
EGRESS_NORMAL_TRAFFIC_TABLE = "p4.Egress.egress_traffic_table"

# ---------------------------------------------------------------------------------------------------
# Ingress VLAN Functions
# ---------------------------------------------------------------------------------------------------

def ingress_vlan_add_with_forward(ingress_port, ether_type, vid, vid_mask, priority, egress_port):
    """Adds an ingress VLAN forward rule."""
    return f"{INGRESS_VLAN_TRAFFIC_TABLE}.add_with_forward(ingress_port={ingress_port}, \n\t\t\tether_type=\"{ether_type}\", \n\t\t\tvid={vid}, \n\t\t\tvid_mask={vid_mask}, \n\t\t\tMATCH_PRIORITY={priority}, \n\t\t\tegress_port={egress_port})"

def ingress_vlan_add_with_swap_vlan_id(ingress_port, ether_type, vid, vid_mask, new_vid, egress_port):
    """Adds an ingress VLAN swap VLAN ID rule."""
    return f"{INGRESS_VLAN_TRAFFIC_TABLE}.add_with_swap_vlan_id(ingress_port={ingress_port}, \n\t\t\tether_type=\"{ether_type}\", \n\t\t\tvid={vid}, \n\t\t\tvid_mask={vid_mask}, \n\t\t\tnew_vid={new_vid}, \n\t\t\tegress_port={egress_port})"

def ingress_vlan_add_with_swap_vlan(ingress_port, ether_type, vid, vid_mask, new_vid, new_ether_type, egress_port):
    """Adds an ingress VLAN swap VLAN rule."""
    return f"{INGRESS_VLAN_TRAFFIC_TABLE}.add_with_swap_vlan(ingress_port={ingress_port}, \n\t\t\tether_type=\"{ether_type}\", \n\t\t\tvid={vid}, \n\t\t\tvid_mask={vid_mask}, \n\t\t\tnew_vid={new_vid}, \n\t\t\tnew_ether_type='{new_ether_type}', \n\t\t\tegress_port={egress_port})"

def ingress_vlan_add_with_pop_outer_vlan(ingress_port, ether_type, vid, vid_mask, priority, egress_port):
    """Adds an ingress VLAN pop outer VLAN rule."""
    return f"{INGRESS_VLAN_TRAFFIC_TABLE}.add_with_pop_outer_vlan(ingress_port={ingress_port}, \n\t\t\tether_type=\"{ether_type}\", \n\t\t\tvid={vid}, \n\t\t\tvid_mask={vid_mask}, \n\t\t\tMATCH_PRIORITY={priority}, \n\t\t\tegress_port={egress_port})"

# ---------------------------------------------------------------------------------------------------
# Ingress Normal Functions
# ---------------------------------------------------------------------------------------------------

def ingress_normal_add_with_push_outer_vlan(ingress_port, new_vid, new_ether_type, egress_port):
    """Adds an ingress normal push outer VLAN rule."""
    return f"{INGRESS_NORMAL_TRAFFIC_TABLE}.add_with_push_outer_vlan(ingress_port={ingress_port}, \n\t\t\tnew_vid={new_vid}, \n\t\t\tnew_ether_type='{new_ether_type}', \n\t\t\tegress_port={egress_port})"
    # return f"{INGRESS_NORMAL_TRAFFIC_TABLE}.add_with_push_outer_vlan(ingress_port={ingress_port}, \n\t\t\tucast_egress_port={egress_port}, \n\t\t\tnew_vid={new_vid}, \n\t\t\tnew_ether_type='{new_ether_type}', \n\t\t\tegress_port={egress_port})"

def ingress_normal_add_with_forward(ingress_port, egress_port):
    """Adds an ingress normal forward rule."""
    return f"{INGRESS_NORMAL_TRAFFIC_TABLE}.add_with_forward(ingress_port={ingress_port}, \n\t\t\tegress_port={egress_port})"
    # return f"{INGRESS_NORMAL_TRAFFIC_TABLE}.add_with_forward(ingress_port={ingress_port}, \n\t\t\tucast_egress_port={egress_port}, \n\t\t\tegress_port={egress_port})"


# ---------------------------------------------------------------------------------------------------
# Egress VLAN Functions
# ---------------------------------------------------------------------------------------------------

def egress_vlan_add_with_shift_int(egress_port, ether_type, vid, vid_mask, priority):
    """Adds an egress VLAN shift INT rule."""
    return f"{EGRESS_VLAN_TRAFFIC_TABLE}.add_with_shift_int(egress_port={egress_port}, \n\t\t\tether_type=\"{ether_type}\", \n\t\t\tvid={vid}, \n\t\t\tvid_mask={vid_mask}, \n\t\t\tMATCH_PRIORITY={priority})"

def egress_vlan_add_with_push_int(egress_port, ether_type, vid, vid_mask, priority):
    """Adds an egress VLAN push INT rule."""
    return f"{EGRESS_VLAN_TRAFFIC_TABLE}.add_with_push_int(egress_port={egress_port}, \n\t\t\tether_type=\"{ether_type}\", \n\t\t\tvid={vid}, \n\t\t\tvid_mask={vid_mask}, \n\t\t\tMATCH_PRIORITY={priority})"

def egress_vlan_add_with_pop_and_vlan(egress_port, ether_type, vid, vid_mask, priority, new_vid):
    """Adds an egress VLAN pop and VLAN rule."""
    return f"{EGRESS_VLAN_TRAFFIC_TABLE}.add_with_pop_and_vlan(egress_port={egress_port}, \n\t\t\tether_type=\"{ether_type}\", \n\t\t\tvid={vid}, \n\t\t\tvid_mask={vid_mask}, \n\t\t\tMATCH_PRIORITY={priority}, \n\t\t\tnew_vid={new_vid})"

# ---------------------------------------------------------------------------------------------------
# Egress Normal Functions
# ---------------------------------------------------------------------------------------------------

def egress_normal_add_with_pop_int(egress_port, ether_type):
    """Adds an egress normal pop INT rule."""
    return f"{EGRESS_NORMAL_TRAFFIC_TABLE}.add_with_pop_int(egress_port={egress_port}, \n\t\t\tether_type='{ether_type}')"

def egress_normal_add_with_pop_int_and_add_vlan(egress_port, ether_type, new_vid, new_ether_type):
    """Adds an egress normal pop INT and add VLAN rule."""
    return f"{EGRESS_NORMAL_TRAFFIC_TABLE}.add_with_pop_int_and_add_vlan(egress_port={egress_port}, \n\t\t\tether_type=\"{ether_type}\", new_vid={new_vid}, \n\t\t\tnew_ether_type='{new_ether_type}')"

# ---------------------------------------------------------------------------------------------------
# Packet Processing Functions
# ---------------------------------------------------------------------------------------------------

def swap_vlan(received_pkt, c_vlan, s_vlan):
    """Swaps VLAN by modifying the received packet."""
    received_pkt[0] = "eth(0x88a8)"
    received_pkt.insert(1, f"s-vlan({s_vlan},0x8100)")
    return received_pkt

def int_count_f(received_pkt):
    """Counts the number of INT headers in the packet."""
    return sum('int' in s for s in received_pkt) + 1

def push_int(received_pkt, c_vlan, s_vlan):
    """Pushes an INT header onto the packet."""
    vlan_type = received_pkt[1].split(",")[1].split(")")[0]
    received_pkt[1] = f"s-vlan({s_vlan},0x601)"
    int_count = int_count_f(received_pkt)
    received_pkt.insert(2, f"int{int_count}({vlan_type})")
    return received_pkt

def swap_vlan_id(received_pkt, c_vlan, s_vlan, s):
    """Swaps VLAN ID in the received packet based on conditions."""
    ether_type = received_pkt[1].split(",")[1].split(")")[0]
    if s:
        received_pkt[0] = "eth(0x88a8)"
        received_pkt[1] = f"s-vlan({s_vlan + 1},{ether_type})"
    else:
        received_pkt[0] = "eth(0x8100)"
        received_pkt[1] = f"c-vlan({c_vlan + 1},{ether_type})"
    return received_pkt

def shift_int(received_pkt, c_vlan, s_vlan):
    """Shifts an INT header in the packet."""
    int_count = int_count_f(received_pkt)
    received_pkt.insert(2, f"int{int_count}({received_pkt[1].split(',')[1].split(')')[0]})")
    return received_pkt

def pop_outer_vlan(received_pkt, c_vlan, s_vlan):
    """Removes the outer VLAN from the packet."""
    received_pkt.pop(1)
    received_pkt[0] = "eth(0x601)"
    return received_pkt

def pop_int(received_pkt, c_vlan, s_vlan):
    """Pops the INT header from the packet."""
    int1_index = next((i for i, element in enumerate(received_pkt) if "int1" in element), -1)
    if int1_index != -1:
        int1_type = received_pkt[int1_index].split("(")[1].split(")")[0]
        received_pkt.pop(int1_index)
        received_pkt[0] = f"eth({int1_type})"
    return [element for element in received_pkt if "int" not in element]

def forward(received_pkt, c_vlan, s_vlan):
    """Forwards the packet unchanged."""
    return received_pkt

def nothing(received_pkt, c_vlan, s_vlan):
    """Does nothing to the packet."""
    return received_pkt

def pop_and_vlan(received_pkt, c_vlan, s_vlan):
    """Pops the INT header and converts the packet to a VLAN format."""
    received_pkt = pop_int(received_pkt, c_vlan, s_vlan)
    received_pkt = pop_outer_vlan(received_pkt, c_vlan, s_vlan)
    ether_type = received_pkt[1].split(",")[1].split(")")[0]
    vid = int(received_pkt[1].split(",")[0].split("(")[1])
    received_pkt[0] = f"eth(0x8100)"
    received_pkt[1] = f"c-vlan({vid + 1},{ether_type})"
    return received_pkt

def push_outer_vlan(received_pkt, c_vlan, s_vlan, s):
    """Pushes an outer VLAN header onto the packet."""
    ether_type = received_pkt[0].split("(")[1].split(")")[0]
    if s:
        received_pkt[0] = "eth(0x88a8)"
        received_pkt.insert(1, f"s-vlan({s_vlan},{ether_type})")
    else:
        received_pkt[0] = "eth(0x8100)"
        received_pkt.insert(1, f"c-vlan({c_vlan},{ether_type})")
    return received_pkt

def pop_int_and_add_vlan(received_pkt, c_vlan, s_vlan):
    """Pops INT and adds a VLAN to the packet."""
    received_pkt = pop_int(received_pkt, c_vlan, s_vlan)
    ether_type = received_pkt[0].split("(")[1].split(")")[0]
    received_pkt.insert(1, f"c-vlan({c_vlan},{ether_type})")
    received_pkt[0] = "eth(0x8100)"
    return received_pkt



def first_switch(user1, user1_port, user2, user2_port, links, use_case, vlan_c_ids, vlan_s_ids):
    #printf"Processing Use Case: {use_case}")
    
    # Define the default packet structures based on the use case
    if use_case in ["No VLAN translation", "VLAN translation", "With VLAN range (No translation)"]:
        ingress_pkt_incoming = [f"eth(0x8100)", f"c-vlan({vlan_c_ids[0]},0x800)", "IPv4", "UDP", "Payload"]
    else:
        ingress_pkt_incoming = [f"eth(0x800)", "IPv4", "UDP", "Payload"]

    # Mapping of use cases to configurations
    config_map = {
        "With VLAN range (No translation)": {
            "ingress_entry": lambda: ingress_vlan_add_with_swap_vlan(user1_port, "0x8100", vlan_c_ids[0], "0xFF", vlan_s_ids[0], "0x88a8", links[1]),
            "egress_entry": lambda: egress_vlan_add_with_push_int(links[1], "0x88a8", vlan_s_ids[0], "0xFF", 20),
            "ingress_out": lambda pkt: swap_vlan(pkt, vlan_c_ids[0], vlan_s_ids[0]),
            "egress_out": lambda pkt: push_int(pkt, vlan_c_ids[0], vlan_s_ids[0]),
            "actions": (pop_outer_vlan, pop_int)
        },
        "VLAN translation": {
            "ingress_entry": lambda: ingress_vlan_add_with_swap_vlan(user1_port, "0x8100", vlan_c_ids[0], "0xFF", vlan_s_ids[0], "0x88a8", links[1]),
            "egress_entry": lambda: egress_vlan_add_with_push_int(links[1], "0x88a8", vlan_s_ids[0], "0xFF", 20),
            "ingress_out": lambda pkt: swap_vlan(pkt, vlan_c_ids[0], vlan_s_ids[0]),
            "egress_out": lambda pkt: shift_int(pkt, vlan_c_ids[0], vlan_s_ids[0]),
            "actions": (forward, pop_and_vlan)
        },
        "No VLAN": {
            "ingress_entry": lambda: ingress_normal_add_with_push_outer_vlan(user1_port, vlan_s_ids[0], "0x88a8", links[1]),
            "egress_entry": lambda: egress_vlan_add_with_push_int(links[1], "0x88a8", vlan_s_ids[0], "0xFF", 20),
            "ingress_out": lambda pkt: push_outer_vlan(pkt, vlan_c_ids[0], vlan_s_ids[0], True),
            "egress_out": lambda pkt: push_int(pkt, vlan_c_ids[0], vlan_s_ids[0]),
            "actions": (pop_outer_vlan, pop_int)
        },
        "No VLAN U1 with VLAN U2": {
            "ingress_entry": lambda: ingress_normal_add_with_push_outer_vlan(user1_port, vlan_s_ids[0], "0x88a8", links[1]),
            "egress_entry": lambda: egress_vlan_add_with_push_int(links[1], "0x88a8", vlan_s_ids[0], "0xFF", 20),
            "ingress_out": lambda pkt: push_outer_vlan(pkt, vlan_c_ids[0], vlan_s_ids[0], True),
            "egress_out": lambda pkt: push_int(pkt, vlan_c_ids[0], vlan_s_ids[0]),
            "actions": (pop_outer_vlan, pop_int_and_add_vlan)
        },
        "No VLAN translation": {
            "ingress_entry": lambda: ingress_vlan_add_with_swap_vlan(user1_port, "0x8100", vlan_c_ids[0], "0xFF", vlan_s_ids[0], "0x88a8", links[1]),
            "egress_entry": lambda: egress_vlan_add_with_push_int(links[1], "0x88a8", vlan_s_ids[0], "0xFF", 20),
            "ingress_out": lambda pkt: swap_vlan(pkt, vlan_c_ids[0], vlan_s_ids[0]),
            "egress_out": lambda pkt: push_int(pkt, vlan_c_ids[0], vlan_s_ids[0]),
            "actions": (pop_outer_vlan, pop_int)
        }
    }

    # Retrieve the configuration for the current use case
    config = config_map.get(use_case)
    if config:
        # Process entries and packets based on the use case configuration
        ingress_entry = config["ingress_entry"]()
        egress_entry = config["egress_entry"]()
        
        ingress_pkt_outgoing = config["ingress_out"](ingress_pkt_incoming.copy())
        egress_pkt_incoming = ingress_pkt_outgoing
        egress_pkt_outgoing = config["egress_out"](egress_pkt_incoming.copy())  
        last_ingress_action, last_egress_action = config["actions"]
        temp_in_out.append(ingress_pkt_incoming)
        temp_in_out.append(ingress_pkt_outgoing)
        temp_in_out.append(egress_pkt_incoming)
        temp_in_out.append(egress_pkt_outgoing)
            
        # Display results
        #printf"{user1}({user1_port})<->{links[0]}({links[1]})")
        print_entries_pkt(ingress_entry, egress_entry, ingress_pkt_incoming, ingress_pkt_outgoing, egress_pkt_incoming, egress_pkt_outgoing, f"{user1}({user1_port})<->{links[0]}({links[1]})")
        return last_ingress_action, last_egress_action, egress_pkt_outgoing,ingress_pkt_incoming
    else:
        print(f"Unknown use case: {use_case}")


def intermediate_switch(user1, user1_port, user2, user2_port, links, use_case, vlan_c_ids, vlan_s_ids, last_ingress_action, last_egress_action,first_sw_egress_pkt):

    for i in range(len(links)-1):
        ingress_entry = ingress_vlan_add_with_swap_vlan_id(links[i][2], "0x88a8", vlan_s_ids[0], "0xFF", vlan_s_ids[0]+1, links[i+1][1])
        egress_entry = egress_vlan_add_with_shift_int(links[i+1][1],"0x88a8", vlan_s_ids[0]+1, "0xFF", 20)
        ingress_pkt_incoming = first_sw_egress_pkt.copy()
        ingress_pkt_outgoing = swap_vlan_id(ingress_pkt_incoming.copy(), vlan_s_ids[0], vlan_s_ids[0], True)
        egress_pkt_incoming = ingress_pkt_outgoing.copy()
        egress_pkt_outgoing = shift_int(egress_pkt_incoming.copy(), vlan_s_ids[0], vlan_s_ids[0])
        temp_in_out.append(ingress_pkt_incoming)
        temp_in_out.append(ingress_pkt_outgoing)
        temp_in_out.append(egress_pkt_incoming)
        temp_in_out.append(egress_pkt_outgoing)
        print_entries_pkt(ingress_entry, egress_entry, ingress_pkt_incoming, ingress_pkt_outgoing, egress_pkt_incoming, egress_pkt_outgoing, f"{links[i][0]}({links[i][2]})<->{links[i+1][0]}({links[i+1][1]})")
        vlan_s_ids[0] += 1
    return egress_pkt_outgoing, vlan_s_ids[0]

def last_switch(user1, user1_port, user2, user2_port, links, use_case, vlan_c_ids, vlan_s_ids, last_ingress_action, last_egress_action,prior_sw_egress_pkt):
    # Last packet processing
    if(last_ingress_action == pop_outer_vlan):
        ingress_entry = ingress_vlan_add_with_pop_outer_vlan(links[-1][2],"0x88a8", vlan_s_ids,"0xFF",20,user2_port)
    else:
        ingress_entry = ingress_vlan_add_with_forward(links[-1][2],"0x88a8",vlan_s_ids,"0xFF",20,user2_port)
    ingress_pkt_incoming = prior_sw_egress_pkt.copy()
    ingress_pkt_outgoing = last_ingress_action(ingress_pkt_incoming.copy(), vlan_c_ids[0], vlan_s_ids)
    if(last_egress_action == pop_int):
        egress_entry = egress_normal_add_with_pop_int(user2_port,"0x601")
    elif(last_egress_action == pop_and_vlan):
        egress_entry = egress_vlan_add_with_pop_and_vlan(user2_port,"0x88a8",vlan_s_ids,"0xFF",20,vlan_c_ids[0]+1)
    else:
        egress_entry = egress_normal_add_with_pop_int_and_add_vlan(user2_port,"0x601",vlan_c_ids[0],"0x8100")
    
    egress_pkt_incoming = ingress_pkt_outgoing.copy()
    egress_pkt_outgoing = last_egress_action(egress_pkt_incoming.copy(), vlan_c_ids[0], vlan_s_ids)
    temp_in_out.append(ingress_pkt_incoming)
    temp_in_out.append(ingress_pkt_outgoing)
    temp_in_out.append(egress_pkt_incoming)
    temp_in_out.append(egress_pkt_outgoing)

    print_entries_pkt(ingress_entry, egress_entry, ingress_pkt_incoming, ingress_pkt_outgoing, egress_pkt_incoming, egress_pkt_outgoing, f"{links[-1][0]}({links[-1][2]})<->{user2}({user2_port})")


def handle_multiple_switches(etherType, route):
    user1, user1_port, user2, user2_port, links, use_case, vlan_c_ids, vlan_s_ids = route
    last_ingress_action, last_egress_action,egress_pkt_outgoing,ingress_pkt_incoming = first_switch(user1, user1_port, user2, user2_port, links[0], use_case, vlan_c_ids, vlan_s_ids)
    egress_pkt_outgoing, vlan_s_ids = intermediate_switch(user1, user1_port, user2, user2_port, links, use_case, vlan_c_ids, vlan_s_ids, last_ingress_action, last_egress_action,egress_pkt_outgoing)
    last_switch(user1, user1_port, user2, user2_port, links, use_case, vlan_c_ids, vlan_s_ids, last_ingress_action, last_egress_action,egress_pkt_outgoing)
    return ingress_pkt_incoming


def print_entries_pkt(ingress_entry, egress_entry, ingress_pkt_incoming, ingress_pkt_outgoing, egress_pkt_incoming, egress_pkt_outgoing,end_point):
    """
    Utility function to print entries and packets in a structured format.
    """
    add_entry(end_point, ingress_entry, egress_entry, ingress_pkt_incoming, egress_pkt_outgoing)


def add_entry(endpoint, ingress_entry, egress_entry, ingress_pkt_incoming, egress_pkt_outgoing):
    """
    Appends the entry to the entries file.
    """
    append_pkts(ingress_pkt_incoming, egress_pkt_outgoing)
    if ingress_entry in existing_entries:
        print(f"Entry already exists: {ingress_entry}")
    else:
        existing_entries.add(ingress_entry)
        append_to_file(f"\n# {endpoint}\n")
        append_to_file("\n    " + ingress_entry + "\n")
    if egress_entry in existing_entries:
        print(f"Entry already exists: {egress_entry}")
        return
    else:
        existing_entries.add(egress_entry)
        append_to_file("\n    " + egress_entry + "\n")

    


def handle_single_switch(etherType, route):
    user1, user1_port, user2, user2_port, links, use_case, vlan_c_ids, vlan_s_ids = route
    #printuser1, user1_port, user2, user2_port, links, use_case, vlan_c_ids, vlan_s_ids)
    # Default Packet Structures
    common_ingress_pkt = [f"eth({etherType})", "IPv4", "UDP", "Payload"]
    vlan_pkt = common_ingress_pkt.copy()
    vlan_pkt.insert(1, f"c-vlan({vlan_c_ids[0]},0x800)")
    
    # Set up based on use case
    use_case_actions = {
        "No VLAN translation": {
            "ingress_entry": lambda: ingress_vlan_add_with_forward(user1_port, etherType, vlan_c_ids[0], "0xFF", 20, user2_port),
            "packet_in": vlan_pkt,
            "process_out": lambda pkt: forward(pkt, vlan_c_ids[0], vlan_s_ids[0])
        },
        "With VLAN range (No translation)": {
            "ingress_entry": lambda: ingress_vlan_add_with_forward(user1_port, etherType, vlan_c_ids[0], "0xFF0", 20, user2_port),
            "packet_in": vlan_pkt,
            "process_out": lambda pkt: forward(pkt, vlan_c_ids[0], vlan_s_ids[0])
        },
        "No VLAN U1 with VLAN U2": {
            "ingress_entry": lambda: ingress_normal_add_with_push_outer_vlan(user1_port, vlan_c_ids[0], "0x8100", user2_port),
            "packet_in": common_ingress_pkt,
            "process_out": lambda pkt: push_outer_vlan(pkt, vlan_c_ids[0], vlan_s_ids[0], False)
        },
        "VLAN translation": {
            "ingress_entry": lambda: ingress_vlan_add_with_swap_vlan_id(user1_port, "0x8100", vlan_c_ids[0], "0xFF", vlan_c_ids[0] + 1, user2_port),
            "packet_in": vlan_pkt,
            "process_out": lambda pkt: swap_vlan_id(pkt, vlan_c_ids[0], vlan_s_ids[0], False)
        },
        "No VLAN": {
            "ingress_entry": lambda: ingress_normal_add_with_forward(user1_port, user2_port),
            "packet_in": common_ingress_pkt,
            "process_out": lambda pkt: forward(pkt, vlan_c_ids[0], vlan_s_ids[0])
        }
    }
    
    # Process the selected use case
    if use_case in use_case_actions:
        config = use_case_actions[use_case]
        ingress_entry = config["ingress_entry"]()
        egress_entry = ""
        ingress_pkt_incoming = config["packet_in"].copy()
        ingress_pkt_outgoing = config["process_out"](ingress_pkt_incoming.copy())
        egress_pkt_incoming = ingress_pkt_outgoing
        egress_pkt_outgoing = nothing(egress_pkt_incoming.copy(), vlan_c_ids[0], vlan_s_ids[0])
        temp_in_out.append(ingress_pkt_incoming)
        temp_in_out.append(egress_pkt_outgoing)

        print_entries_pkt(ingress_entry, egress_entry, ingress_pkt_incoming, ingress_pkt_outgoing, egress_pkt_incoming, egress_pkt_outgoing,f"{user1}({user1_port})<->{user2}({user2_port})")
    else:
        print(f"Unknown use case: {use_case}")
        return
    
    return ingress_pkt_incoming


def process_route(route):
    # Extract route details
    user1,user1_port,user2,user2_port,links,use_case,vlan_c_ids,vlan_s_ids = route
    etherType = "0x8100" if use_case in ["No VLAN translation", "VLAN translation","With VLAN range (No translation)"] else "0x800"
    #Single switch
    if len(links)==1:
        pkt = handle_single_switch(etherType,route)
    else:
        pkt = handle_multiple_switches(etherType,route)

    return pkt,user1_port,user2_port



def create_entries_file():
    header_file = 'bfrt_python/entries_header.txt'
    entries_file = 'bfrt_python/entries.py'
    # Always create a fresh entries file
    with open(header_file, 'r') as hf, open(entries_file, 'w') as ef:
        header_content = hf.read()
        ef.write(header_content)
    print("Header content successfully added to entries.py.")

def end_entries_file():
    entries_footer = 'bfrt_python/entries_footer.txt'
    entries_file = 'bfrt_python/entries.py'
    # Append the footer content if not already appended
    with open(entries_file, 'a') as ef, open(entries_footer, 'r') as ff:
        footer_content = ff.read()
        ef.write(footer_content)
    print("Footer content successfully added to entries.py.")

def append_to_file(content):
    entries_file = 'bfrt_python/entries.py'
    with open(entries_file, 'a') as ef:
        ef.write(content)


def append_pkts(incoming_pkt, outgoing_pkt):
    temp = []
    temp.append(incoming_pkt)
    temp.append(outgoing_pkt)
    pkts_in_out.append(temp)

    


def generate_entries(routes):
    pkt_route_details = []
    global pkts_in_out, temp_in_out
    pkts_in_out = []
    create_entries_file()
    for route in routes:
        pkt_port = []
        temp_in_out = []
        append_to_file("\n#------------------------------------------------------------------------------------------------------\n")
        append_to_file(f"#\t{route}\n")
        append_to_file("#------------------------------------------------------------------------------------------------------\n")
        pkt,user1_port,user2_port = process_route(route)
        pkt_port.append(pkt)
        pkt_port.append(user1_port)
        pkt_port.append(user2_port)
        pkt_port.append(route)
        # print("Temp In Out:", temp_in_out)
        pkt_route_details.append(pkt_port)
        
    end_entries_file()
    return pkt_route_details,pkts_in_out

