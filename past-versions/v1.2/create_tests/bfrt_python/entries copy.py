import random

p4 = bfrt.project2.pipe
INGRESS_NO_VLAN_TRAFFIC_TABLE =  p4.Ingress.no_vlan_traffic_table
INGRESS_VLAN_TRAFFIC_TABLE =  p4.Ingress.vlan_traffic_table
EGRESS_S_VLAN_TRAFFIC_TABLE =  p4.Egress.egress_s_vlan_traffic_table
EGRESS_INT_TABLE =  p4.Egress.egress_int_table
EGRESS_NORMAL_TRAFFIC_TABLE =  p4.Egress.egress_normal_traffic_table


# This function can clear all the tables and later on other fixed objects
# once bfrt support is added.
def clear_all(verbose=True, batching=True):
    global p4
    global bfrt

    # The order is important. We do want to clear from the top, i.e.
    # delete objects that use other objects, e.g. table entries use
    # selector groups and selector groups use action profile members

    for table_types in (['MATCH_DIRECT', 'MATCH_INDIRECT_SELECTOR'],
                        ['SELECTOR'],
                        ['ACTION_PROFILE']):
        for table in p4.info(return_info=True, print_info=False):
            if table['type'] in table_types:
                if verbose:
                    print("Clearing table {:<40} ... ".
                          format(table['full_name']), end='', flush=True)
                table['node'].clear(batch=batching)
                if verbose:
                    print('Done')

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
    INGRESS_NO_VLAN_TRAFFIC_TABLE =  p4.Ingress.no_vlan_traffic_table
    INGRESS_VLAN_TRAFFIC_TABLE =  p4.Ingress.vlan_traffic_table
    EGRESS_S_VLAN_TRAFFIC_TABLE =  p4.Egress.egress_s_vlan_traffic_table

    #Case1 Ingress
    INGRESS_VLAN_TRAFFIC_TABLE.add_with_forward(
        ingress_port=0,
        vid=10,
        ether_type=0x8100,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        egress_port=1
    )

    #Case2 Ingress
    INGRESS_VLAN_TRAFFIC_TABLE.add_with_forward(
        ingress_port=0,
        vid=20,
        ether_type=0x8100,
        vid_mask=0xFF0,
        MATCH_PRIORITY=20,
        egress_port=1
    )    

    #Case3 Ingress
    INGRESS_NO_VLAN_TRAFFIC_TABLE.add_with_add_u_vlan(
        ingress_port=0,
        new_vid=30,
        egress_port=1
    )
    
    #Case4 Ingress
    INGRESS_VLAN_TRAFFIC_TABLE.add_with_modify_u_vlan(
        vid=40,
        ingress_port=0,
        ether_type=0x8100,
        vid_mask=0x0FFF,
        new_vid=41,
        egress_port=1
    )

    #Case5a Ingress
    INGRESS_VLAN_TRAFFIC_TABLE.add_with_forward(
        ingress_port=0,
        vid=50,
        ether_type=0x8100,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        egress_port=3
    )

    #Case5a Egress
    EGRESS_S_VLAN_TRAFFIC_TABLE.add_with_swap_outer_vlan(
        egress_port=3,
        ether_type=0x8100,
        vid=50,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        new_vid=501
    )


    #Case5b Ingress
    INGRESS_VLAN_TRAFFIC_TABLE.add_with_forward(
        ingress_port=4,
        vid=501,
        ether_type=0x88a8,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        egress_port=7
    )

    #Case5b Egress
    EGRESS_S_VLAN_TRAFFIC_TABLE.add_with_modify_s_vlan(
        egress_port=7,
        ether_type=0x88a8,
        vid=501,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        new_vid=502
    )

    #Case5c Ingress
    INGRESS_VLAN_TRAFFIC_TABLE.add_with_forward(
        ingress_port=8,
        vid=502,
        ether_type=0x88a8,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        egress_port=2
    )
    #Case5c Egress
    EGRESS_S_VLAN_TRAFFIC_TABLE.add_with_swap_vlans_rm_int(
        egress_port=2,
        ether_type=0x88a8,
        vid=502,
        vid_mask=0xFF,
        MATCH_PRIORITY=20
    )

    #Case6a Ingress
    INGRESS_VLAN_TRAFFIC_TABLE.add_with_modify_u_vlan(
        vid=60,
        ingress_port=0,
        ether_type=0x8100,
        vid_mask=0xFF,
        new_vid=61,
        egress_port=3
    )

    #Case6a Egress
    EGRESS_S_VLAN_TRAFFIC_TABLE.add_with_swap_outer_vlan(
        egress_port=3,
        ether_type=0x8100,
        vid=61,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        new_vid=601
    )

    #Case6b Ingress
    INGRESS_VLAN_TRAFFIC_TABLE.add_with_forward(
        ingress_port=4,
        vid=601,
        ether_type=0x88a8,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        egress_port=7
    )

    #Case6b Egress
    EGRESS_S_VLAN_TRAFFIC_TABLE.add_with_modify_s_vlan(
        egress_port=7,
        ether_type=0x88a8,
        vid=601,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        new_vid=602
    )


    #Case6c Ingress
    INGRESS_VLAN_TRAFFIC_TABLE.add_with_forward(
        ingress_port=8,
        vid=602,
        ether_type=0x88a8,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        egress_port=2
    )

    #Case6c Egress
    EGRESS_S_VLAN_TRAFFIC_TABLE.add_with_swap_vlans_rm_int(
        egress_port=2,
        ether_type=0x88a8,
        vid=602,
        vid_mask=0xFF,
        MATCH_PRIORITY=20
    )

    #Case7a Ingress
    INGRESS_NO_VLAN_TRAFFIC_TABLE.add_with_forward(
        ingress_port=1,
        egress_port=5
    )

    #Case7a Egress
    EGRESS_NORMAL_TRAFFIC_TABLE.add_with_add_s_vlan(
        egress_port=5,
        new_vid=701
    )


    #Case7b Ingress
    INGRESS_VLAN_TRAFFIC_TABLE.add_with_forward(
        ingress_port=6,
        vid=701,
        ether_type=0x88a8,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        egress_port=9
    )

    #Case7b Egress
    EGRESS_S_VLAN_TRAFFIC_TABLE.add_with_modify_s_vlan(
        egress_port=9,
        ether_type=0x88a8,
        vid=701,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        new_vid=702
    )

    #Case7c Ingress
    INGRESS_VLAN_TRAFFIC_TABLE.add_with_forward(
        ingress_port=10,
        vid=702,
        ether_type=0x88a8,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        egress_port=2
    )

    #Case7c Egress
    EGRESS_S_VLAN_TRAFFIC_TABLE.add_with_rm_s_vlan_rm_int(
        egress_port=2,
        ether_type=0x88a8,
        vid=702,
        vid_mask=0xFF,
        MATCH_PRIORITY=20
    )

    #Case8a Ingress
    INGRESS_NO_VLAN_TRAFFIC_TABLE.add_with_add_u_vlan(
        ingress_port=2,
        new_vid=80,
        egress_port=9
    )

    #Case8a Egress
    EGRESS_S_VLAN_TRAFFIC_TABLE.add_with_swap_outer_vlan(
        egress_port=9,
        ether_type=0x8100,
        vid=80,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        new_vid=801
    )

    #Case8b Ingress
    INGRESS_VLAN_TRAFFIC_TABLE.add_with_forward(
        ingress_port=10,
        vid=801,
        ether_type=0x88a8,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        egress_port=5
    )

    #Case8b Egress
    EGRESS_S_VLAN_TRAFFIC_TABLE.add_with_modify_s_vlan(
        egress_port=5,
        ether_type=0x88a8,
        vid=801,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        new_vid=802
    )

    #Case8c Ingress
    INGRESS_VLAN_TRAFFIC_TABLE.add_with_forward(
        ingress_port=6,
        vid=802,
        ether_type=0x88a8,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        egress_port=1
    )

    #Case8c Egress
    EGRESS_S_VLAN_TRAFFIC_TABLE.add_with_swap_vlans_rm_int(
        egress_port=1,
        ether_type=0x88a8,
        vid=802,
        vid_mask=0xFF,
        MATCH_PRIORITY=20
    )












    print("Done")
    print("INGRESS_NO_VLAN_TRAFFIC_TABLE")
    print(INGRESS_NO_VLAN_TRAFFIC_TABLE.dump())
    print("INGRESS_VLAN_TRAFFIC_TABLE")
    print(INGRESS_VLAN_TRAFFIC_TABLE.dump())
    print("EGRESS_S_VLAN_TRAFFIC_TABLE")
    print(EGRESS_S_VLAN_TRAFFIC_TABLE.dump())
    print("EGRESS_INT_TABLE")
    print(EGRESS_INT_TABLE.dump())
    print("EGRESS_NORMAL_TRAFFIC_TABLE")
    print(EGRESS_NORMAL_TRAFFIC_TABLE.dump())
    

clear_all()
create_entries()
print("""
*** Run this script in the interactive mode
***
*** Use create_entries() to test the capacity of a multi-way hash table.
*** Use clear_all() to clear the tables
*** Use help(<function>) to learn more
""")