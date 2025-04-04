import random

p4 = bfrt.p4_v1_1.pipe

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
    IngressVlanTrafficTable = p4.Ingress.ingress_vlan_traffic_table
    IngressNormalTrafficTable = p4.Ingress.ingress_normal_traffic_table
    EgressNormalTrafficTable = p4.Egress.egress_traffic_table
    EgressVlanTrafficTable = p4.Egress.egress_vlan_traffic_table
#------------------------------------------------------------------------------------------------------
#	['u3', 9, 'u1', 1, [['sw6-sw5', 11, 12], ['sw5-sw3', 13, 14], ['sw3-sw1', 15, 16]], 'With VLAN range (No translation)', [70], [701]]
#------------------------------------------------------------------------------------------------------

# u3(9)<->sw6-sw5(11)

    p4.Ingress.ingress_vlan_traffic_table.add_with_swap_vlan(ingress_port=9, 
			ether_type="0x8100", 
			vid=70, 
			vid_mask=0xFF, 
			new_vid=701, 
			new_ether_type='0x88a8', 
			egress_port=11)

    p4.Egress.egress_vlan_traffic_table.add_with_push_int(egress_port=11, 
			ether_type="0x88a8", 
			vid=701, 
			vid_mask=0xFF, 
			MATCH_PRIORITY=20)

# sw6-sw5(12)<->sw5-sw3(13)

    p4.Ingress.ingress_vlan_traffic_table.add_with_swap_vlan_id(ingress_port=12, 
			ether_type="0x88a8", 
			vid=701, 
			vid_mask=0xFF, 
			new_vid=702, 
			egress_port=13)

    p4.Egress.egress_vlan_traffic_table.add_with_shift_int(egress_port=13, 
			ether_type="0x88a8", 
			vid=702, 
			vid_mask=0xFF, 
			MATCH_PRIORITY=20)

# sw5-sw3(14)<->sw3-sw1(15)

    p4.Ingress.ingress_vlan_traffic_table.add_with_swap_vlan_id(ingress_port=14, 
			ether_type="0x88a8", 
			vid=702, 
			vid_mask=0xFF, 
			new_vid=703, 
			egress_port=15)

    p4.Egress.egress_vlan_traffic_table.add_with_shift_int(egress_port=15, 
			ether_type="0x88a8", 
			vid=703, 
			vid_mask=0xFF, 
			MATCH_PRIORITY=20)

# sw3-sw1(16)<->u1(1)

    p4.Ingress.ingress_vlan_traffic_table.add_with_pop_outer_vlan(ingress_port=16, 
			ether_type="0x88a8", 
			vid=703, 
			vid_mask=0xFF, 
			MATCH_PRIORITY=20, 
			egress_port=1)

    p4.Egress.egress_traffic_table.add_with_pop_int(egress_port=1, 
			ether_type='0x601')

#------------------------------------------------------------------------------------------------------
#	['u2', 8, 'u1', 1, [['sw6-sw5', 11, 12], ['sw5-sw3', 13, 14], ['sw3-sw1', 15, 16]], 'No VLAN U1 with VLAN U2', [80], [801]]
#------------------------------------------------------------------------------------------------------

# u2(8)<->sw6-sw5(11)

    p4.Ingress.ingress_normal_traffic_table.add_with_push_outer_vlan(ingress_port=8, 
			new_vid=801, 
			new_ether_type='0x88a8', 
			egress_port=11)

    p4.Egress.egress_vlan_traffic_table.add_with_push_int(egress_port=11, 
			ether_type="0x88a8", 
			vid=801, 
			vid_mask=0xFF, 
			MATCH_PRIORITY=20)

# sw6-sw5(12)<->sw5-sw3(13)

    p4.Ingress.ingress_vlan_traffic_table.add_with_swap_vlan_id(ingress_port=12, 
			ether_type="0x88a8", 
			vid=801, 
			vid_mask=0xFF, 
			new_vid=802, 
			egress_port=13)

    p4.Egress.egress_vlan_traffic_table.add_with_shift_int(egress_port=13, 
			ether_type="0x88a8", 
			vid=802, 
			vid_mask=0xFF, 
			MATCH_PRIORITY=20)

# sw5-sw3(14)<->sw3-sw1(15)

    p4.Ingress.ingress_vlan_traffic_table.add_with_swap_vlan_id(ingress_port=14, 
			ether_type="0x88a8", 
			vid=802, 
			vid_mask=0xFF, 
			new_vid=803, 
			egress_port=15)

    p4.Egress.egress_vlan_traffic_table.add_with_shift_int(egress_port=15, 
			ether_type="0x88a8", 
			vid=803, 
			vid_mask=0xFF, 
			MATCH_PRIORITY=20)

# sw3-sw1(16)<->u1(1)

    p4.Ingress.ingress_vlan_traffic_table.add_with_pop_outer_vlan(ingress_port=16, 
			ether_type="0x88a8", 
			vid=803, 
			vid_mask=0xFF, 
			MATCH_PRIORITY=20, 
			egress_port=1)

    p4.Egress.egress_traffic_table.add_with_pop_int_and_add_vlan(egress_port=1, 
			ether_type="0x601", new_vid=80, 
			new_ether_type='0x8100')

#------------------------------------------------------------------------------------------------------
#	['u3', 9, 'u1', 1, [['sw6-sw5', 11, 12], ['sw5-sw3', 13, 14], ['sw3-sw1', 15, 16]], 'VLAN translation', [90], [901]]
#------------------------------------------------------------------------------------------------------

# u3(9)<->sw6-sw5(11)

    p4.Ingress.ingress_vlan_traffic_table.add_with_swap_vlan(ingress_port=9, 
			ether_type="0x8100", 
			vid=90, 
			vid_mask=0xFF, 
			new_vid=901, 
			new_ether_type='0x88a8', 
			egress_port=11)

    p4.Egress.egress_vlan_traffic_table.add_with_push_int(egress_port=11, 
			ether_type="0x88a8", 
			vid=901, 
			vid_mask=0xFF, 
			MATCH_PRIORITY=20)

# sw6-sw5(12)<->sw5-sw3(13)

    p4.Ingress.ingress_vlan_traffic_table.add_with_swap_vlan_id(ingress_port=12, 
			ether_type="0x88a8", 
			vid=901, 
			vid_mask=0xFF, 
			new_vid=902, 
			egress_port=13)

    p4.Egress.egress_vlan_traffic_table.add_with_shift_int(egress_port=13, 
			ether_type="0x88a8", 
			vid=902, 
			vid_mask=0xFF, 
			MATCH_PRIORITY=20)

# sw5-sw3(14)<->sw3-sw1(15)

    p4.Ingress.ingress_vlan_traffic_table.add_with_swap_vlan_id(ingress_port=14, 
			ether_type="0x88a8", 
			vid=902, 
			vid_mask=0xFF, 
			new_vid=903, 
			egress_port=15)

    p4.Egress.egress_vlan_traffic_table.add_with_shift_int(egress_port=15, 
			ether_type="0x88a8", 
			vid=903, 
			vid_mask=0xFF, 
			MATCH_PRIORITY=20)

# sw3-sw1(16)<->u1(1)

    p4.Ingress.ingress_vlan_traffic_table.add_with_forward(ingress_port=16, 
			ether_type="0x88a8", 
			vid=903, 
			vid_mask=0xFF, 
			MATCH_PRIORITY=20, 
			egress_port=1)

    p4.Egress.egress_vlan_traffic_table.add_with_pop_and_vlan(egress_port=1, 
			ether_type="0x88a8", 
			vid=903, 
			vid_mask=0xFF, 
			MATCH_PRIORITY=20, 
			new_vid=91)

#------------------------------------------------------------------------------------------------------
#	['u1', 1, 'u4', 10, [['sw1-sw2', 2, 3], ['sw2-sw4', 4, 5], ['sw4-sw6', 6, 7]], 'No VLAN', [100], [1001]]
#------------------------------------------------------------------------------------------------------

# u1(1)<->sw1-sw2(2)

    p4.Ingress.ingress_normal_traffic_table.add_with_push_outer_vlan(ingress_port=1, 
			new_vid=1001, 
			new_ether_type='0x88a8', 
			egress_port=2)

    p4.Egress.egress_vlan_traffic_table.add_with_push_int(egress_port=2, 
			ether_type="0x88a8", 
			vid=1001, 
			vid_mask=0xFF, 
			MATCH_PRIORITY=20)

# sw1-sw2(3)<->sw2-sw4(4)

    p4.Ingress.ingress_vlan_traffic_table.add_with_swap_vlan_id(ingress_port=3, 
			ether_type="0x88a8", 
			vid=1001, 
			vid_mask=0xFF, 
			new_vid=1002, 
			egress_port=4)

    p4.Egress.egress_vlan_traffic_table.add_with_shift_int(egress_port=4, 
			ether_type="0x88a8", 
			vid=1002, 
			vid_mask=0xFF, 
			MATCH_PRIORITY=20)

# sw2-sw4(5)<->sw4-sw6(6)

    p4.Ingress.ingress_vlan_traffic_table.add_with_swap_vlan_id(ingress_port=5, 
			ether_type="0x88a8", 
			vid=1002, 
			vid_mask=0xFF, 
			new_vid=1003, 
			egress_port=6)

    p4.Egress.egress_vlan_traffic_table.add_with_shift_int(egress_port=6, 
			ether_type="0x88a8", 
			vid=1003, 
			vid_mask=0xFF, 
			MATCH_PRIORITY=20)

# sw4-sw6(7)<->u4(10)

    p4.Ingress.ingress_vlan_traffic_table.add_with_pop_outer_vlan(ingress_port=7, 
			ether_type="0x88a8", 
			vid=1003, 
			vid_mask=0xFF, 
			MATCH_PRIORITY=20, 
			egress_port=10)

    p4.Egress.egress_traffic_table.add_with_pop_int(egress_port=10, 
			ether_type='0x601')
    print("Done")
    print("Table IngressVlanTrafficTable")
    print(IngressVlanTrafficTable.dump())
    print("IngressNormalTrafficTable")
    print(IngressNormalTrafficTable.dump())
    print("EgressNormalTrafficTable")
    print(EgressNormalTrafficTable.dump())
    print("EgressVlanTrafficTable")
    print(EgressVlanTrafficTable.dump())

clear_all()
create_entries()
print("""
*** Run this script in the interactive mode
***
*** Use create_entries() to test the capacity of a multi-way hash table.
*** Use clear_all() to clear the tables
*** Use help(<function>) to learn more
""")