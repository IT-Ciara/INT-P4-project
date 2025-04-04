

p4 = bfrt.p4_v1_3.pipe

def clear_all(verbose=True, batching=True):
    """
    Clears all the tables in the P4 pipeline, skipping unsupported tables.
    """
    global p4

    unsupported_tables = ['pipe.Egress.egress_int_table']

    # The order of clearing is important to avoid dependencies
    for table_types in (['MATCH_DIRECT', 'MATCH_INDIRECT_SELECTOR'],
                        ['SELECTOR'],
                        ['ACTION_PROFILE']):
        for table in p4.info(return_info=True, print_info=False):
            if table['type'] in table_types:
                table_name = table['full_name']
                if table_name in unsupported_tables:
                    if verbose:
                        print(f"Skipping table {table_name} as it does not support clearing.")
                    continue

                try:
                    if verbose:
                        print(f"Clearing table {table_name:<40} ... ", end='', flush=True)
                    table['node'].clear(batch=batching)
                    if verbose:
                        print('Done')
                except Exception as e:
                    if verbose:
                        print(f"Failed to clear table {table_name}: {e}")



def create_entries():
    """
    Fill in ipv4_host table with random entries, determined by using the
    provided function until failure

    Keyword arguments:
    keyfunc  -- A function that gets "count" as an arg and returns the
                IP address for that entry (default is use count)
    batching -- Batch all the commands (default is True)

    Examples:  create_entries(lambda c: randint(0, 0xFFFFFFFF), True)
               create_entries(lambda c: c + 0xC0a80101, True)
    """
    global p4
    global random
    global clear_all

    # Traffic Table Names
    INGRESS_NO_VLAN_TRAFFIC_TABLE = p4.Ingress.no_vlan_traffic_table
    INGRESS_VLAN_TRAFFIC_TABLE = p4.Ingress.vlan_traffic_table

    INGRESS_NO_VLAN_TRAFFIC_TABLE.add_with_forward(ingress_port=0, egress_port=1)

    INGRESS_VLAN_TRAFFIC_TABLE.add_with_forward(vid=1000, vid_mask=0xFF, ingress_port=0, ether_type=0x88a8, MATCH_PRIORITY=20, egress_port=1)






    print("Done")
    print("INGRESS_NO_VLAN_TRAFFIC_TABLE")
    print(INGRESS_NO_VLAN_TRAFFIC_TABLE.dump())
    print("INGRESS_VLAN_TRAFFIC_TABLE")
    print(INGRESS_VLAN_TRAFFIC_TABLE.dump())
    

clear_all()
create_entries()
print("""
*** Run this script in the interactive mode
***
*** Use create_entries() to test the capacity of a multi-way hash table.
*** Use clear_all() to clear the tables
*** Use help(<function>) to learn more
""")