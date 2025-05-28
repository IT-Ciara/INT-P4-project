
import bfrt_grpc.client as gc

#=======================================================================================================================
"""
Utility functions for creating and managing table entries in a P4 pipeline.
These functions handle the creation, modification, and deletion of entries in various stages of the pipeline,
as well as the management of indirect counters.
This module provides functions to:
- Clear all entries from specified stages and their associated tables and indirect counters.
- Create key entries based on packet values and table definitions.
- Create action data based on selected actions and case details.
- Print all entries from a given table in a readable format.
- Fetch all entries from a specified table and return them as a list of tuples.
- Create entries in specified stages based on case details and packet information.
"""
#=======================================================================================================================



#========================================== C O N S T A N T S =========================================================
#=======================================================================================================================
S_VLAN = 900
U_VLAN = 200

#========================================== C R E A T E  E N T R I E S =================================================
#=======================================================================================================================

def clear_all(stages, dev_tgt, bfrt_info):
    """
    Clear all entries from the specified stages and their associated tables and indirect counters.
    :param stages: Dictionary containing stage information.
    :param dev_tgt: Device target for the BFRT operations.
    :param bfrt_info: BFRT information object.
    """
    for stage, data in stages.items():
        for tbl_name in data['Tables']:
            if 'eg_int_table' in tbl_name:
                continue
            table = bfrt_info.table_get(tbl_name)
            table.entry_del(dev_tgt, [])
        for ctr_name in data['Indirect Counters']:
            table = bfrt_info.table_get(ctr_name)
            table.entry_del(dev_tgt, [])

def create_key(case, tbl, dev_tgt, bfrt_info,case_pkt,pkt,selected_action):
    """
    Create a key entry based on the provided case, table, and packet.
    :param case: Dictionary containing packet values and other case details.
    :param tbl: Dictionary containing table details.
    :param dev_tgt: Device target for the BFRT operations.
    :param bfrt_info: BFRT information object.
    :param case_pkt: Packet values from the case.
    :param pkt: The actual packet being processed.
    :param selected_action: The action selected for the table.
    :return: A list of KeyTuple objects representing the key entry.
    """

    key_entry = None
    key_entry_list = []
    value_int = 0
    for key in tbl['keys']:
        value = 0
        if '.ingress_port' in key['name']:
            value = case['pkt_values']['ig_intr_md.ingress_port']
        elif 'egress_port' in key['name']:
            value = case['pkt_values']['ig_tm_md.ucast_egress_port']
        elif 'ethernet.ether_type' in key['name']:
            value = pkt.getlayer('Ether').type
            if value == int(0x88a8) and "Egress" in selected_action.get('name'):
                value = pkt.getlayer('Dot1AD').type
                case['pkt_values']['hdr.ethernet.ether_type'] = hex(value)
        elif '$MATCH_PRIORITY' in key['name']:
            value = 10                
        elif 'u_vlan.vid' in key['name']:
            #Check if the packet has a Dot1Q layer
            if pkt.haslayer('Dot1Q'):
                value = pkt.getlayer('Dot1Q').vlan
        elif 's_vlan.vid' in key['name']:
            if selected_action.get('name').startswith('Ingress.'):
                if pkt.haslayer('Dot1AD'):
                    value = pkt.getlayer('Dot1AD').vlan
        else:
            value = case['pkt_values'][key['name']]
        if isinstance(value, str) and ':' in value:
            # Remove colons and convert hex string to int
            value_int = int(value.replace(':', ''), 16)
        # Check if the value is an IP address (contains dots)
        elif isinstance(value, str) and '.' in value:
            # Convert IP address to int
            value_int = int.from_bytes([int(octet) for octet in value.split('.')], 'big')
        # Check if the value is a hexadecimal string (starts with 0x)
        elif isinstance(value, str) and value.startswith('0x'):
            # Convert hex string to int
            value_int = int(value, 16)
        else:
            # Fall back to normal int conversion
            value_int = int(value)  
          
        if key['match'].lower() == "exact":
            key_entry_list.append(gc.KeyTuple(key['name'], value_int))
        elif key['match'].lower() == "ternary":
            if value_int == 0:
                key_entry_list.append(gc.KeyTuple(key['name'], value_int,0x0))
            else:
                key_entry_list.append(gc.KeyTuple(key['name'], value_int,0xFF))
    return key_entry_list        

def create_action_data(action,case, tbl, dev_tgt, bfrt_info,case_pkt,pkt):
    """
    Create action data based on the provided action and case.
    :param action: Dictionary containing action details.
    :param case: Dictionary containing packet values and other case details.
    :param tbl: Dictionary containing table details.
    :param dev_tgt: Device target for the BFRT operations.
    :param bfrt_info: BFRT information object.
    :param case_pkt: Packet values from the case.
    :param pkt: The actual packet being processed.
    :return: A list of DataTuple objects representing the action data.
    """

    action_data_list = []
    if "Egress.set_port_md" in action['name']:
        user_port, p4_sw_port, transit_port = (1, 0, 0) if "User" in case["Output"] else (0, 1, 0) if "P4" in case["Output"] else (0, 0, 1) if "Transit" in case["Output"] else (0, 0, 0)
        action_data_list.append(gc.DataTuple("user_port", user_port))
        action_data_list.append(gc.DataTuple("p4_sw_port", p4_sw_port))
        action_data_list.append(gc.DataTuple("transit_port", transit_port))
    if "Ingress.set_port_md" in action['name']:
        user_port = 1 
        action_data_list.append(gc.DataTuple("user_port", user_port))
        action_data_list.append(gc.DataTuple("egress_port", int(case['pkt_values']['ig_tm_md.ucast_egress_port'])))
    else:
        for parameter in action['parameters']:
            if parameter == 'egress_port':
                action_data_list.append(gc.DataTuple(parameter, int(case['pkt_values']['ig_tm_md.ucast_egress_port'])))
            elif parameter == "ing_mir":
                action_data_list.append(gc.DataTuple(parameter, 1))
            elif parameter == 'ing_ses':
                action_data_list.append(gc.DataTuple(parameter, int(case['pkt_values']['hdr_ing_ses'])))
            elif parameter == 'new_vid':
                if "add_s_vlan" in action['name']:
                    action_data_list.append(gc.DataTuple(parameter, int(S_VLAN)))
                elif "add_u_vlan" in action['name']:
                    action_data_list.append(gc.DataTuple(parameter, int(case_pkt['hdr_new_vid'])))
                elif "modify_u_vlan" in action['name']:
                    action_data_list.append(gc.DataTuple(parameter, int(case_pkt['hdr_new_vid'])))
    return action_data_list

def print_all_entries(table, dev_tgt, bfrt_info,print_details=False):
    """
    Print all entries from a given table in a readable format.
    :param table: The table object from which to fetch entries.
    :param dev_tgt: Device target for the BFRT operations.
    :param bfrt_info: BFRT information object.
    :param print_details: Boolean flag to control detailed printing.
    """

    table_name = table.info.name_get()
    if print_details:
        print(f"\n=== Table: {table_name} ===")
    
    for data, key in table.entry_get(dev_tgt, [], {"from_hw": True}):
        key_dict = key.to_dict()
        data_dict = data.to_dict()
        # Extract the action name
        action = data_dict.pop('action_name', 'N/A')
        if print_details:
            print("Keys:")
            for k, v in key_dict.items():
                val = v.get("value", v)  # fallback in case "value" is missing
                print(f"  {k:<35}: {val}")
        if print_details:
            print(f"Action: {action}")
        
        # Print Parameters (excluding action_name, is_default_entry, counters)
        if print_details:
            print("Parameters:")
            for param, val in data_dict.items():
                if param in ("is_default_entry", "$COUNTER_SPEC_PKTS"):
                    continue
                print(f"  {param:<20}: {val}")

        # Optionally, show counters and flags
        counter = data_dict.get("$COUNTER_SPEC_PKTS")
        if print_details:
            if counter is not None:
                print(f"Counter Packets        : {counter}")
            
        if print_details:
            print("\n" + "-" * 60 + "\n")


def get_all_entries(table_name, dev_tgt, bfrt_info):
    """
    Fetch all entries from a specified table and return them as a list of tuples.
    :param table_name: Name of the table to fetch entries from.
    :param dev_tgt: Device target for the BFRT operations.
    :param bfrt_info: BFRT information object.
    :return: A list of tuples, each containing a key and its corresponding data.
    """
        
    table = bfrt_info.table_get(table_name)
    entries = []
    for data, key in table.entry_get(dev_tgt, [], {"from_hw": True}):
        entries.append((key.to_dict(), data.to_dict()))
    return entries

def create_entry(action, case, tbl, dev_tgt, bfrt_info,pkt, print_details=False):
    """
    Create an entry in the specified table with the given action and case details.
    :param action: Dictionary containing action details.
    :param case: Dictionary containing packet values and other case details.
    :param tbl: Dictionary containing table details.
    :param dev_tgt: Device target for the BFRT operations.
    :param bfrt_info: BFRT information object.
    :param pkt: The actual packet being processed.
    :param print_details: Boolean flag to control detailed printing.
    """

    table = bfrt_info.table_get(tbl['grpc_name'])
    key_entry_list = create_key(case, tbl, dev_tgt, bfrt_info, case['pkt_values'],pkt,action)
    key_entry = table.make_key(key_entry_list)

    action_data_list = create_action_data(action, case, tbl, dev_tgt, bfrt_info, case['pkt_values'],pkt)
    action_data = table.make_data(action_data_list,action_name=action['name'])

    table.entry_add(dev_tgt,[key_entry],[action_data])
    print_all_entries(table, dev_tgt, bfrt_info, print_details=print_details)

def filter_actions(actions, include_keywords=None, exclude_keywords=None):
    """
    Filter actions based on include and exclude keywords.
    :param actions: List of action dictionaries to filter.
    :param include_keywords: List of keywords that must be present in the action name.
    :param exclude_keywords: List of keywords that must not be present in the action name.
    :return: Filtered list of actions.
    """

    filtered = actions
    if include_keywords:
        filtered = [act for act in filtered if any(kw in act['name'] for kw in include_keywords)]
    if exclude_keywords:
        filtered = [act for act in filtered if all(kw not in act['name'] for kw in exclude_keywords)]
    return filtered

def select_action(case,tbl,dev_tgt, bfrt_info,pkt, print_details=False):
    """
    Select the appropriate action based on the table and case details.
    :param case: Dictionary containing packet values and other case details.
    :param tbl: Dictionary containing table details.
    :param dev_tgt: Device target for the BFRT operations.
    :param bfrt_info: BFRT information object.
    :param pkt: The actual packet being processed.
    :param print_details: Boolean flag to control detailed printing.
    """

    table_name = tbl.get('name') or tbl.get('grpc_name','').split('.')[-1]
    action = None
    if len(tbl['actions']) == 1:
        action = tbl['actions'][0]
        create_entry(action, case, tbl, dev_tgt, bfrt_info, pkt, print_details=print_details)
    elif len(tbl['actions']) > 1:
        #==================================================================================
        #=====================I N G R E S S   T A B L E S ==================================
        #=================================================================================
        if table_name == 'ig_partner_provided_link_tbl':
            if case['pkt_values']['hdr.ethernet.ether_type'].lower() == "0x88a8":
                action = next((act for act in tbl['actions'] if 's_vlan' in act['name']), None)
                create_entry(action, case, tbl, dev_tgt, bfrt_info, pkt, print_details=print_details)

        #=================================================================================
        #=====================E G R E S S   T A B L E S ==================================
        #=================================================================================
        #=====================E G  T R A N S I T  P O R T  T B L =========================
        elif table_name == 'eg_transit_port_tbl':
            if case['pkt_values']['hdr.ethernet.ether_type'] == "0x8842":
                #Find the action which contains polka
                action = next((act for act in tbl['actions'] if 'polka' in act['name']), None)
                create_entry(action, case, tbl, dev_tgt, bfrt_info, pkt, print_details=print_details)
            else:
                action = next((act for act in tbl['actions'] if 'polka' not in act['name']), None)
                create_entry(action, case, tbl, dev_tgt, bfrt_info, pkt, print_details=print_details)
        #===================E G  U S E R  S W I T C H  P O R T  T B L ======================
        elif table_name == 'eg_user_port_tbl':
            endpoint_action = case['stage_tables']['Stg10 | Endpoint action'].get('value')
            if case['pkt_values']['hdr.ethernet.ether_type'] == "0x8842":
                next_hdr = hex(pkt.getlayer('CustomINTShim').next_hdr)
                #Filter out the action which contains polka
                actions = filter_actions(tbl['actions'], include_keywords=['polka'])
                if endpoint_action == "add vlan":
                    if next_hdr == "0x800":
                        action = next((act for act in actions if 'add_u_vlan' in act['name']), None)
                        create_entry(action, case, tbl, dev_tgt, bfrt_info, pkt, print_details=print_details)
                elif endpoint_action == "no vlan":
                    if next_hdr == "0x8100":
                        action = next((act for act in actions if 'rm_polka_int_u_vlan' in act['name']), None)
                        create_entry(action, case, tbl, dev_tgt, bfrt_info, pkt, print_details=print_details)
                    elif next_hdr == "0x800":
                        action = next((act for act in actions if act['name'].endswith('rm_polka_int')), None)
                        create_entry(action, case, tbl, dev_tgt, bfrt_info, pkt, print_details=print_details)
                elif endpoint_action == "vlan translation":
                    if next_hdr == "0x8100":
                        action = next((act for act in actions if 'modify_u_vlan' in act['name']), None)
                        create_entry(action, case, tbl, dev_tgt, bfrt_info, pkt, print_details=print_details)
            else:
                actions = filter_actions(tbl['actions'], exclude_keywords=['polka', 's_vlan'])
                if endpoint_action == "add vlan":
                    action = next((act for act in actions if 'add_u_vlan' in act['name']), None)
                    create_entry(action, case, tbl, dev_tgt, bfrt_info, pkt, print_details=print_details)
                elif endpoint_action == "no vlan":
                    if case['pkt_values']['hdr.ethernet.ether_type'] == "0x88a8":
                        if pkt.getlayer('Dot1AD').type == 0x8100:
                            action = next((act for act in actions if 'rm_u_vlan' in act['name']), None)
                            create_entry(action, case, tbl, dev_tgt, bfrt_info, pkt)
                    elif case['pkt_values']['hdr.ethernet.ether_type'] == "0x8100":
                        action = next((act for act in actions if 'rm_u_vlan' in act['name']), None)
                        create_entry(action, case, tbl, dev_tgt, bfrt_info, pkt, print_details=print_details)

                elif endpoint_action == "vlan translation":
                    if case['pkt_values']['hdr.ethernet.ether_type'] == "0x88a8" or case['pkt_values']['hdr.ethernet.ether_type'] == "0x8100":
                        if pkt.haslayer('Dot1AD'):
                            if pkt.getlayer('Dot1AD').type == 0x8100:
                                action = next((act for act in actions if 'modify_u_vlan' in act['name']), None)
                                create_entry(action, case, tbl, dev_tgt, bfrt_info, pkt, print_details=print_details)
                        else:
                            action = next((act for act in actions if 'modify_u_vlan' in act['name']), None)
                            create_entry(action, case, tbl, dev_tgt, bfrt_info, pkt, print_details=print_details)                  

        elif table_name == 'eg_p4_sw_port_tbl':
            if case['pkt_values']['hdr.ethernet.ether_type'].lower() == 0x88a8:
                action = next((act for act in tbl['actions'] if 's_vlan' in act['name']), None)
                create_entry(action, case, tbl, dev_tgt, bfrt_info, pkt, print_details=print_details)
            else:
                action = next((act for act in tbl['actions'] if 's_vlan' not in act['name']), None)
                create_entry(action, case, tbl, dev_tgt, bfrt_info, pkt,print_details=print_details)

def create_entries_main(case, dev_tgt, bfrt_info, pkt,print_details=False):
    """
    Create entries in the specified stages based on the case details.
    :param case: Dictionary containing packet values and other case details.
    :param dev_tgt: Device target for the BFRT operations.
    :param bfrt_info: BFRT information object.
    :param pkt: The actual packet being processed.
    :param print_details: Boolean flag to control detailed printing.
    """

    for stage, stage_data in case['stage_tables'].items():
        
        if stage_data['value'] == "YES":
            tables_dict = stage_data.get("Tables", {})
            num_tables = len(tables_dict)

            if num_tables >= 1:
                table_list = list(tables_dict.values())  # ✅ Convert dict to list

                if num_tables > 1:
                    ether_type = case['pkt_values'].get('hdr.ethernet.ether_type')
                    if ether_type == 0x8842 or ether_type == "0x8842":
                        continue
                    else:
                        selected_table = None
                        for tbl in table_list:
                            if "eg_p4_sw_port_tbl" in tbl.get("grpc_name", ""):
                                selected_table = tbl
                                break
                        if selected_table:
                            tbl = selected_table
                        else:
                            print(f"⚠️ No matching table found in stage {stage}")
                            continue
                else:  # Exactly one table
                    tbl = table_list[0]

                # Proceed with entry creation
                select_action(case, tbl, dev_tgt, bfrt_info, pkt, print_details=print_details)

