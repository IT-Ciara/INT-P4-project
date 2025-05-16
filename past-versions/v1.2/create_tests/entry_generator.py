import os 

existing_entries = set()

#-----------------------------------------------------------------------------------------------------------
# TRAFFIC TABLE NAMES
#-----------------------------------------------------------------------------------------------------------
INGRESS_VLAN_TRAFFIC_TABLE = "p4.Ingress.vlan_traffic_table"
INGRESS_NO_VLAN_TRAFFIC_TABLE = "p4.Ingress.no_vlan_traffic_table"
EGRESS_INT_TABLE = "p4.Egress.egress_int_table"
EGRESS_NORMAL_TRAFFIC_TABLE = "p4.Egress.egress_normal_traffic_table"
EGRESS_S_VLAN_TRAFFIC_TABLE = "p4.Egress.egress_s_vlan_traffic_table"

#-----------------------------------------------------------------------------------------------------------
# INGRESS TABLES
#-----------------------------------------------------------------------------------------------------------
#------- VLAN TABLE ACTIONS -------
INGRESS_VLAN_TRAFFIC_TABLE_ACTIONS = ['modify_u_vlan','forward']
#-------- NO VLAN TABLE ACTIONS -------
INGRESS_NO_VLAN_TRAFFIC_TABLE_ACTIONS = ['forward','add_u_vlan']

#-----------------------------------------------------------------------------------------------------------
# EGRESS TABLES
#-----------------------------------------------------------------------------------------------------------
#------- EGRESS INT TABLE ACTIONS -------
EGRESS_INT_TABLE_ACTIONS = ['push_int1','push_int2','push_int3','push_int4','push_int5','increase_int_count']
#------- EGRESS NORMAL TRAFFIC ACTIONS -------
EGRESS_NORMAL_TRAFFIC_TABLE_ACTIONS = ['remove_int','swap_inner_to_outer_vlan','swap_vlans_rm_int','add_s_vlan']
#------- EGRESS S VLAN TRAFFIC ACTIONS -------
EGRESS_S_VLAN_TRAFFIC_TABLE_ACTIONS = ['swap_outer_vlan','add_int_shim','push_int0','modify_s_vlan','remove_int','swap_inner_to_outer_vlan','swap_vlans_rm_int','rm_s_vlan','rm_s_vlan_rm_int']

#-----------------------------------------------------------------------------------------------------------
# INGRESS TABLES FUNCTIONS
#-----------------------------------------------------------------------------------------------------------

def ingress_vlan_add_with_forward(ingress_port,vid,ether_type,vid_mask,MATCH_PRIORITY,egress_port):
    return f"{INGRESS_VLAN_TRAFFIC_TABLE}.add_with_forward(\n\
        ingress_port={ingress_port},\n\
        vid={vid},\n\
        ether_type={ether_type},\n\
        vid_mask={vid_mask},\n\
        MATCH_PRIORITY={MATCH_PRIORITY},\n\
        egress_port={egress_port}\n\
    )"

def ingress_vlan_add_with_modify_u_vlan(ingress_port,vid,ether_type,vid_mask,MATCH_PRIORITY,new_vid,egress_port):
    return f"{INGRESS_VLAN_TRAFFIC_TABLE}.add_with_modify_u_vlan(\n\
        ingress_port={ingress_port},\n\
        vid={vid},\n\
        ether_type={ether_type},\n\
        vid_mask={vid_mask},\n\
        MATCH_PRIORITY={MATCH_PRIORITY},\n\
        new_vid={new_vid},\n\
        egress_port={egress_port}\n\
    )"

def ingress_normal_add_with_forward(ingress_port,egress_port):
    return f"{INGRESS_NO_VLAN_TRAFFIC_TABLE}.add_with_forward(\n\
        ingress_port={ingress_port},\n\
        egress_port={egress_port}\n\
    )"

def ingress_normal_add_with_add_u_vlan(ingress_port,new_vid,egress_port):
    return f"{INGRESS_NO_VLAN_TRAFFIC_TABLE}.add_with_add_u_vlan(\n\
        ingress_port={ingress_port},\n\
        new_vid={new_vid},\n\
        egress_port={egress_port}\n\
    )"

#-----------------------------------------------------------------------------------------------------------
# EGRESS TABLES FUNCTIONS
#-----------------------------------------------------------------------------------------------------------

def egress_normal_add_with_add_s_vlan(egress_port,new_vid):
    return f"{EGRESS_NORMAL_TRAFFIC_TABLE}.add_with_add_s_vlan(\n\
        egress_port={egress_port},\n\
        new_vid={new_vid}\n\
    )"


def egress_s_vlan_add_with_swap_outer_vlan(egress_port,ether_type,vid,vid_mask,MATCH_PRIORITY,new_vid):
    return f"{EGRESS_S_VLAN_TRAFFIC_TABLE}.add_with_swap_outer_vlan(\n\
        egress_port={egress_port},\n\
        ether_type={ether_type},\n\
        vid={vid},\n\
        vid_mask={vid_mask},\n\
        MATCH_PRIORITY={MATCH_PRIORITY},\n\
        new_vid={new_vid}\n\
    )"

def egress_s_vlan_add_with_modify_s_vlan(egress_port,ether_type,vid,vid_mask,MATCH_PRIORITY,new_vid):
    return f"{EGRESS_S_VLAN_TRAFFIC_TABLE}.add_with_modify_s_vlan(\n\
        egress_port={egress_port},\n\
        ether_type={ether_type},\n\
        vid={vid},\n\
        vid_mask={vid_mask},\n\
        MATCH_PRIORITY={MATCH_PRIORITY},\n\
        new_vid={new_vid}\n\
    )"

def egress_s_vlan_add_with_swap_vlans_rm_int(egress_port,ether_type,vid,vid_mask,MATCH_PRIORITY):
    return f"{EGRESS_S_VLAN_TRAFFIC_TABLE}.add_with_swap_vlans_rm_int(\n\
        egress_port={egress_port},\n\
        ether_type={ether_type},\n\
        vid={vid},\n\
        vid_mask={vid_mask},\n\
        MATCH_PRIORITY={MATCH_PRIORITY}\n\
    )"

def egress_s_vlan_add_with_rm_s_vlan_rm_int(egress_port,ether_type,vid,vid_mask,MATCH_PRIORITY):
    return f"{EGRESS_S_VLAN_TRAFFIC_TABLE}.add_with_rm_s_vlan_rm_int(\n\
        egress_port={egress_port},\n\
        ether_type={ether_type},\n\
        vid={vid},\n\
        vid_mask={vid_mask},\n\
        MATCH_PRIORITY={MATCH_PRIORITY}\n\
    )"
     

#-----------------------------------------------------------------------------------------------------------
# PACKET PROCESSING FUNCTIONS
#-----------------------------------------------------------------------------------------------------------

#*-- INGRESS --*#
def forward(received_pkt,c_vlan,s_vlan):
    """Forward the packet to the next switch."""
    return received_pkt

def modify_u_vlan(received_pkt,c_vlan,s_vlan):
    """Modify the c-vlan to s-vlan."""
    # Extract the ether type from vlan tag 
    vlan_type = received_pkt[1].split('(')[1].split(',')[1][:-1]
    #modify u-vlan
    received_pkt[1] = f"u-vlan({c_vlan},{vlan_type})"
    return received_pkt

def add_u_vlan(received_pkt,c_vlan,s_vlan):
    """Add s-vlan to the packet."""
    #extract ether type
    ether_type = received_pkt[0][4:-1]
    #add u-vlan
    received_pkt.insert(1,f"u-vlan({c_vlan},{ether_type})")
    received_pkt[0] = f"eth(0x8100)"    
    return received_pkt

#*-- EGRESS --*#

def add_s_vlan(received_pkt,c_vlan,s_vlan):
    """Add s-vlan to the packet."""
    #extract ether type
    ether_type = received_pkt[0][4:-1]
    received_pkt[0] = f"eth(0x88a8)"
    received_pkt.insert(1,f"s-vlan({s_vlan},{ether_type})")
    received_pkt = add_int_shim(received_pkt,c_vlan,s_vlan)
    return received_pkt

def modify_s_vlan(received_pkt, c_vlan, s_vlan):
    """Modify the c-vlan to s-vlan."""
    # Extract and update the VLAN type
    try:
        vlan_type = received_pkt[1].split('(')[1].split(',')[1][:-1]
        received_pkt[1] = f"s-vlan({s_vlan},{vlan_type})"
    except IndexError:
        raise ValueError("Malformed VLAN entry in received_pkt[1]")
    # Extract the INT count and next header
    try:
        int_count = int(received_pkt[2].split('(')[1].split(',')[0])
        int_next_hdr = received_pkt[2].split('(')[1].split(',')[1][:-1]
    except (IndexError, ValueError):
        raise ValueError("Malformed INT shim entry in received_pkt[2]")
    # Determine which INT push function to call
    received_pkt = push_int(received_pkt, c_vlan, s_vlan, int_count+1)
    # Update the INT shim with the incremented count
    received_pkt[2] = f"int_shim({int_count + 1},{int_next_hdr})"
    return received_pkt


def rm_s_vlan_rm_int(received_pkt,c_vlan,s_vlan):
    """Remove s-vlan and increment the int count."""
    #extract int shim next header
    int_next_hdr = received_pkt[2].split('(')[1].split(',')[1][:-1]
    received_pkt[0] = f"eth({int_next_hdr})"
    received_pkt = remove_int(received_pkt,c_vlan,s_vlan)
    received_pkt = rm_s_vlan(received_pkt,c_vlan,s_vlan)
    return received_pkt

def swap_outer_vlan(received_pkt,c_vlan,s_vlan):
    """Swap the outer vlan."""
    #extract ether type
    ether_type = received_pkt[0][4:-1]
    received_pkt[0] = f"eth(0x88a8)"
    received_pkt.insert(1,f"s-vlan({s_vlan},{ether_type})")
    received_pkt = add_int_shim(received_pkt,c_vlan,s_vlan)
    
    return received_pkt

def swap_vlans_rm_int(received_pkt,c_vlan,s_vlan):
    """Swap the vlans and increment the int count."""
    #extract int shim next header
    int_next_hdr = received_pkt[2].split('(')[1].split(',')[1][:-1]
    received_pkt[0] = f"eth({int_next_hdr})"
    received_pkt = remove_int(received_pkt,c_vlan,s_vlan)
    received_pkt = swap_inner_to_outer_vlan(received_pkt,c_vlan,s_vlan)
    return received_pkt

#Secondary functions 

def add_int_shim(received_pkt,c_vlan,s_vlan):
    """Add int shim to the packet."""
    #get vlan type
    vlan_type = received_pkt[1].split('(')[1].split(',')[1][:-1]
    received_pkt.insert(2,f"int_shim(1,{vlan_type})")
    received_pkt[1] = f"s-vlan({s_vlan},0x0601)"
    received_pkt = push_int(received_pkt,c_vlan,s_vlan,1)
    return received_pkt

def push_int(received_pkt,c_vlan,s_vlan, int_number):
    """Push int shim to the packet."""
    #get vlan type
    received_pkt.insert(3,f"int{int_number}")
    return received_pkt

def remove_int(received_pkt,c_vlan,s_vlan):
    """Remove int shim from the packet."""
    #remove everything that has int
    received_pkt = [x for x in received_pkt if "int" not in x]
    return received_pkt

def swap_inner_to_outer_vlan(received_pkt,c_vlan,s_vlan):
    """Swap the inner vlan to outer vlan."""
    #extract ether type
    received_pkt.pop(1)
    return received_pkt

def rm_s_vlan(received_pkt,c_vlan,s_vlan):
    """Remove s-vlan from the packet."""
    #extract ether type
    received_pkt.pop(1)
    return received_pkt

#*---------------------------------------------------------------------------------------------------------*#
#*--extra functions--*#
def nothing(received_pkt,c_vlan,s_vlan):
    """Do nothing."""
    return received_pkt

#*---------------- M U L T I P L E   S W I T C H   H A N D L I N G ----------------*#
def first_switch(user1, user1_port, user2, user2_port, links, use_case, vlan_c_ids, vlan_s_ids):   
    # Define the default packet structures based on the use case
    if use_case in ["No VLAN translation", "VLAN translation", "With VLAN range (No translation)"]:
        ingress_pkt_incoming = [f"eth(0x8100)", f"u-vlan({vlan_c_ids[0]},0x800)", "IPv4", "UDP", "Payload"]
    else:
        ingress_pkt_incoming = [f"eth(0x800)", "IPv4", "UDP", "Payload"]

    # Mapping of use cases to configurations
    config_map = {
        "With VLAN range (No translation)": {
            "ingress_entry": lambda: ingress_vlan_add_with_forward(user1_port, vlan_c_ids[0], "0x8100", "0xFF0", 20, links[1]),
            # ingress_vlan_add_with_swap_vlan(user1_port, "0x8100", vlan_c_ids[0], "0xFF", vlan_s_ids[0], "0x88a8", links[1]),
            "egress_entry": lambda: egress_s_vlan_add_with_swap_outer_vlan(links[1], "0x8100", vlan_c_ids[0], "0xFF0", 20, vlan_s_ids[0]),
            "ingress_out": lambda pkt: forward(pkt, vlan_c_ids[0], vlan_s_ids[0]),
            "egress_out": lambda pkt: swap_outer_vlan(pkt, vlan_c_ids[0], vlan_s_ids[0]),
            "final_actions": (forward, swap_vlans_rm_int)
        },
        "VLAN translation": {
            "ingress_entry": lambda: ingress_vlan_add_with_modify_u_vlan(user1_port, vlan_c_ids[0], "0x8100", "0xFF", 20, vlan_c_ids[0]+1, links[1]),
            "egress_entry": lambda: egress_s_vlan_add_with_swap_outer_vlan(links[1], "0x8100", vlan_c_ids[0]+1, "0xFF", 20, vlan_s_ids[0]),
            "ingress_out": lambda pkt: modify_u_vlan(pkt, vlan_c_ids[0]+1, vlan_s_ids[0]),
            "egress_out": lambda pkt: swap_outer_vlan(pkt, vlan_c_ids[0], vlan_s_ids[0]),
            "final_actions": (forward, swap_vlans_rm_int)
        },
        "No VLAN": {
            "ingress_entry": lambda: ingress_normal_add_with_forward(user1_port, links[1]),
            # ingress_normal_add_with_push_outer_vlan(user1_port, vlan_s_ids[0], "0x88a8", links[1]),
            "egress_entry": lambda: egress_normal_add_with_add_s_vlan(links[1], vlan_s_ids[0]),
            # egress_vlan_add_with_push_int(links[1], "0x88a8", vlan_s_ids[0], "0xFF", 20),
            "ingress_out": lambda pkt: forward(pkt, vlan_c_ids[0], vlan_s_ids[0]),
            "egress_out": lambda pkt: add_s_vlan(pkt, vlan_c_ids[0], vlan_s_ids[0]),
            "final_actions": (forward,rm_s_vlan_rm_int)
        },
        "No VLAN U1 with VLAN U2": {
            "ingress_entry": lambda: ingress_normal_add_with_add_u_vlan(user1_port, vlan_c_ids[0], links[1]),
            # ingress_normal_add_with_push_outer_vlan(user1_port, vlan_s_ids[0], "0x88a8", links[1]),
            "egress_entry": lambda: egress_s_vlan_add_with_swap_outer_vlan( links[1], "0x8100", vlan_c_ids[0], "0xFF", 20, vlan_s_ids[0]),
            # egress_vlan_add_with_push_int(links[1], "0x88a8", vlan_s_ids[0], "0xFF", 20),
            "ingress_out": lambda pkt: add_u_vlan(pkt, vlan_c_ids[0], vlan_s_ids[0]),
            "egress_out": lambda pkt: swap_outer_vlan(pkt, vlan_c_ids[0], vlan_s_ids[0]),
            "final_actions": (forward, swap_vlans_rm_int)
        },
        "No VLAN translation": {
            "ingress_entry": lambda: ingress_vlan_add_with_forward(user1_port, vlan_c_ids[0], "0x8100", "0xFF", 20, links[1]),
            "egress_entry": lambda: egress_s_vlan_add_with_swap_outer_vlan(links[1], "0x8100", vlan_c_ids[0], "0xFF", 20, vlan_s_ids[0]),
            "ingress_out": lambda pkt: forward(pkt, vlan_c_ids[0], vlan_s_ids[0]),
            "egress_out": lambda pkt: swap_outer_vlan(pkt, vlan_c_ids[0], vlan_s_ids[0]),
            "final_actions": (forward, swap_vlans_rm_int )
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
        last_ingress_action, last_egress_action = config["final_actions"]
        temp_in_out.append(ingress_pkt_incoming)
        temp_in_out.append(ingress_pkt_outgoing)
        temp_in_out.append(egress_pkt_incoming)
        temp_in_out.append(egress_pkt_outgoing)
            
        print_entries_pkt(ingress_entry, egress_entry, ingress_pkt_incoming, ingress_pkt_outgoing, egress_pkt_incoming, egress_pkt_outgoing, f"{user1}({user1_port})<->{links[0]}({links[1]})")
        return last_ingress_action, last_egress_action, egress_pkt_outgoing,ingress_pkt_incoming
    else:
        print(f"Unknown use case: {use_case}")


def intermediate_switch(user1, user1_port, user2, user2_port, links, use_case, vlan_c_ids, vlan_s_ids, last_ingress_action, last_egress_action,first_sw_egress_pkt):
    for i in range(len(links)-1):
        ingress_entry = ingress_vlan_add_with_forward(links[i][2], vlan_s_ids[0],"0x88a8", "0xFF", 20, links[i+1][1])
        egress_entry = egress_s_vlan_add_with_modify_s_vlan(links[i+1][1],"0x88a8", vlan_s_ids[0], "0xFF", 20, vlan_s_ids[0]+1)
        ingress_pkt_incoming = first_sw_egress_pkt.copy()
        ingress_pkt_outgoing = forward(ingress_pkt_incoming.copy(), vlan_s_ids[0], vlan_s_ids[0])
        egress_pkt_incoming = ingress_pkt_outgoing.copy()
        egress_pkt_outgoing = modify_s_vlan(egress_pkt_incoming.copy(), vlan_s_ids[0], vlan_s_ids[0]+1)
        temp_in_out.append(ingress_pkt_incoming)
        temp_in_out.append(ingress_pkt_outgoing)
        temp_in_out.append(egress_pkt_incoming)
        temp_in_out.append(egress_pkt_outgoing)
        print_entries_pkt(ingress_entry, egress_entry, ingress_pkt_incoming, ingress_pkt_outgoing, egress_pkt_incoming, egress_pkt_outgoing, f"{links[i][0]}({links[i][2]})<->{links[i+1][0]}({links[i+1][1]})")
        vlan_s_ids[0] += 1
    return egress_pkt_outgoing, vlan_s_ids[0]

def last_switch(user1, user1_port, user2, user2_port, links, use_case, vlan_c_ids, vlan_s_ids, last_ingress_action, last_egress_action,prior_sw_egress_pkt):
    # Last packet processing
    if(last_ingress_action == forward):
        ingress_entry = ingress_vlan_add_with_forward(links[-1][2], vlan_s_ids,"0x88a8","0xFF",20,user2_port)
    ingress_pkt_incoming = prior_sw_egress_pkt.copy()
    ingress_pkt_outgoing = last_ingress_action(ingress_pkt_incoming.copy(), vlan_c_ids[0], vlan_s_ids)
    if(last_egress_action == swap_vlans_rm_int):
        egress_entry = egress_s_vlan_add_with_swap_vlans_rm_int(user2_port,"0x88a8",vlan_s_ids,"0xFF",20)
    elif(last_egress_action==rm_s_vlan_rm_int):
        egress_entry = egress_s_vlan_add_with_rm_s_vlan_rm_int(user2_port,"0x88a8",vlan_s_ids,"0xFF",20)
    
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



#*---------------- S I N G L E   S W I T C H   H A N D L I N G ----------------*#
def handle_single_switch(etherType, route):
    user1, user1_port, user2, user2_port, links, use_case, vlan_c_ids, vlan_s_ids = route
    #printuser1, user1_port, user2, user2_port, links, use_case, vlan_c_ids, vlan_s_ids)
    # Default Packet Structures
    common_ingress_pkt = [f"eth({etherType})", "IPv4", "UDP", "Payload"]
    vlan_pkt = common_ingress_pkt.copy()
    vlan_pkt.insert(1, f"u-vlan({vlan_c_ids[0]},0x800)")
    
    # Set up based on use case
    use_case_actions = {
        "No VLAN translation": {
            "ingress_entry": lambda: ingress_vlan_add_with_forward(user1_port, vlan_c_ids[0], etherType, "0xFF", 20, user2_port),
            "packet_in": vlan_pkt,
            "process_out": lambda pkt: nothing(pkt, vlan_c_ids[0], vlan_s_ids[0])
        },
        "With VLAN range (No translation)": {
            "ingress_entry": lambda: ingress_vlan_add_with_forward(user1_port, vlan_c_ids[0], etherType, "0xFF0", 20, user2_port),
            "packet_in": vlan_pkt,
            "process_out": lambda pkt: nothing(pkt, vlan_c_ids[0], vlan_s_ids[0])
        },
        "No VLAN U1 with VLAN U2": {
            "ingress_entry": lambda: ingress_normal_add_with_add_u_vlan(user1_port, vlan_c_ids[0], user2_port),
            "packet_in": common_ingress_pkt,
            "process_out": lambda pkt: add_u_vlan(pkt, vlan_c_ids[0], vlan_s_ids[0])
        },
        "VLAN translation": {
            "ingress_entry": lambda: ingress_vlan_add_with_modify_u_vlan(user1_port, vlan_c_ids[0], etherType, "0xFF", 20, vlan_c_ids[0]+1, user2_port),
            "packet_in": vlan_pkt,
            "process_out": lambda pkt: modify_u_vlan(pkt, vlan_c_ids[0]+1, vlan_s_ids[0])
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





def print_entries_pkt(ingress_entry, egress_entry, ingress_pkt_incoming, ingress_pkt_outgoing, egress_pkt_incoming, egress_pkt_outgoing,end_point):
    """
    Utility function to print entries and packets in a structured format.
    """
    # print(f"Ingress Entry: {ingress_entry}")
    # print(f"Egress Entry: {egress_entry}")
    # print(f"Ingress Packet Incoming: {ingress_pkt_incoming}")
    # print(f"Ingress Packet Outgoing: {ingress_pkt_outgoing}")
    # print(f"Egress Packet Incoming: {egress_pkt_incoming}")
    # print(f"Egress Packet Outgoing: {egress_pkt_outgoing}")

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

    



#-----------------------------------------------------------------------------------------------------------
#*--FILE OPERATIONS--*#
#-----------------------------------------------------------------------------------------------------------

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
        pkt_route_details.append(pkt_port)
        
    end_entries_file()
    return pkt_route_details,pkts_in_out
