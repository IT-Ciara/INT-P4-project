import random

p4 = bfrt.p4_v1_2.pipe

INGRESS_NO_VLAN_TRAFFIC_TABLE =  p4.Ingress.no_vlan_traffic_table
INGRESS_VLAN_TRAFFIC_TABLE =  p4.Ingress.vlan_traffic_table
EGRESS_S_VLAN_TRAFFIC_TABLE =  p4.Egress.egress_s_vlan_traffic_table
EGRESS_INT_TABLE =  p4.Egress.egress_int_table
EGRESS_NORMAL_TRAFFIC_TABLE =  p4.Egress.egress_normal_traffic_table


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
    INGRESS_NO_VLAN_TRAFFIC_TABLE =  p4.Ingress.no_vlan_traffic_table
    INGRESS_VLAN_TRAFFIC_TABLE =  p4.Ingress.vlan_traffic_table
    EGRESS_S_VLAN_TRAFFIC_TABLE =  p4.Egress.egress_s_vlan_traffic_table
#------------------------------------------------------------------------------------------------------
#	['u0', 0, 'u1', 1, [['sw1']], 'No VLAN translation', [10], [101]]
#------------------------------------------------------------------------------------------------------

# u0(0)<->u1(1)

    p4.Ingress.vlan_traffic_table.add_with_forward(
        ingress_port=0,
        vid=10,
        ether_type=0x8100,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        egress_port=1
    )

    

#------------------------------------------------------------------------------------------------------
#	['u0', 0, 'u1', 1, [['sw1']], 'With VLAN range (No translation)', [20], [201]]
#------------------------------------------------------------------------------------------------------

# u0(0)<->u1(1)

    p4.Ingress.vlan_traffic_table.add_with_forward(
        ingress_port=0,
        vid=20,
        ether_type=0x8100,
        vid_mask=0xFF0,
        MATCH_PRIORITY=20,
        egress_port=1
    )

#------------------------------------------------------------------------------------------------------
#	['u0', 0, 'u1', 1, [['sw1']], 'No VLAN U1 with VLAN U2', [30], [301]]
#------------------------------------------------------------------------------------------------------

# u0(0)<->u1(1)

    p4.Ingress.no_vlan_traffic_table.add_with_add_u_vlan(
        ingress_port=0,
        new_vid=30,
        egress_port=1
    )

#------------------------------------------------------------------------------------------------------
#	['u0', 0, 'u1', 1, [['sw1']], 'VLAN translation', [40], [401]]
#------------------------------------------------------------------------------------------------------

# u0(0)<->u1(1)

    p4.Ingress.vlan_traffic_table.add_with_modify_u_vlan(
        ingress_port=0,
        vid=40,
        ether_type=0x8100,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        new_vid=41,
        egress_port=1
    )

#------------------------------------------------------------------------------------------------------
#	['u4', 10, 'u3', 9, [['sw6']], 'No VLAN', [50], [501]]
#------------------------------------------------------------------------------------------------------

# u4(10)<->u3(9)

    p4.Ingress.no_vlan_traffic_table.add_with_forward(
        ingress_port=10,
        egress_port=9
    )

#------------------------------------------------------------------------------------------------------
#	['u2', 8, 'u1', 1, [['sw6-sw5', 11, 12], ['sw5-sw3', 13, 14], ['sw3-sw1', 15, 16]], 'No VLAN translation', [60], [601]]
#------------------------------------------------------------------------------------------------------

# u2(8)<->sw6-sw5(11)

    p4.Ingress.vlan_traffic_table.add_with_forward(
        ingress_port=8,
        vid=60,
        ether_type=0x8100,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        egress_port=11
    )

    p4.Egress.egress_s_vlan_traffic_table.add_with_swap_outer_vlan(
        egress_port=11,
        ether_type=0x8100,
        vid=60,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        new_vid=601
    )

# sw6-sw5(12)<->sw5-sw3(13)

    p4.Ingress.vlan_traffic_table.add_with_forward(
        ingress_port=12,
        vid=601,
        ether_type=0x88a8,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        egress_port=13
    )

    p4.Egress.egress_s_vlan_traffic_table.add_with_modify_s_vlan(
        egress_port=13,
        ether_type=0x88a8,
        vid=601,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        new_vid=602
    )

# sw5-sw3(14)<->sw3-sw1(15)

    p4.Ingress.vlan_traffic_table.add_with_forward(
        ingress_port=14,
        vid=602,
        ether_type=0x88a8,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        egress_port=15
    )

    p4.Egress.egress_s_vlan_traffic_table.add_with_modify_s_vlan(
        egress_port=15,
        ether_type=0x88a8,
        vid=602,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        new_vid=603
    )

# sw3-sw1(16)<->u1(1)

    p4.Ingress.vlan_traffic_table.add_with_forward(
        ingress_port=16,
        vid=603,
        ether_type=0x88a8,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        egress_port=1
    )

    p4.Egress.egress_s_vlan_traffic_table.add_with_swap_vlans_rm_int(
        egress_port=1,
        ether_type=0x88a8,
        vid=603,
        vid_mask=0xFF,
        MATCH_PRIORITY=20
    )

#------------------------------------------------------------------------------------------------------
#	['u3', 9, 'u1', 1, [['sw6-sw5', 11, 12], ['sw5-sw3', 13, 14], ['sw3-sw1', 15, 16]], 'With VLAN range (No translation)', [70], [701]]
#------------------------------------------------------------------------------------------------------

# u3(9)<->sw6-sw5(11)

    p4.Ingress.vlan_traffic_table.add_with_forward(
        ingress_port=9,
        vid=70,
        ether_type=0x8100,
        vid_mask=0xFF0,
        MATCH_PRIORITY=20,
        egress_port=11
    )

    p4.Egress.egress_s_vlan_traffic_table.add_with_swap_outer_vlan(
        egress_port=11,
        ether_type=0x8100,
        vid=70,
        vid_mask=0xFF0,
        MATCH_PRIORITY=20,
        new_vid=701
    )

# sw6-sw5(12)<->sw5-sw3(13)

    p4.Ingress.vlan_traffic_table.add_with_forward(
        ingress_port=12,
        vid=701,
        ether_type=0x88a8,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        egress_port=13
    )

    p4.Egress.egress_s_vlan_traffic_table.add_with_modify_s_vlan(
        egress_port=13,
        ether_type=0x88a8,
        vid=701,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        new_vid=702
    )

# sw5-sw3(14)<->sw3-sw1(15)

    p4.Ingress.vlan_traffic_table.add_with_forward(
        ingress_port=14,
        vid=702,
        ether_type=0x88a8,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        egress_port=15
    )

    p4.Egress.egress_s_vlan_traffic_table.add_with_modify_s_vlan(
        egress_port=15,
        ether_type=0x88a8,
        vid=702,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        new_vid=703
    )

# sw3-sw1(16)<->u1(1)

    p4.Ingress.vlan_traffic_table.add_with_forward(
        ingress_port=16,
        vid=703,
        ether_type=0x88a8,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        egress_port=1
    )

    p4.Egress.egress_s_vlan_traffic_table.add_with_swap_vlans_rm_int(
        egress_port=1,
        ether_type=0x88a8,
        vid=703,
        vid_mask=0xFF,
        MATCH_PRIORITY=20
    )

#------------------------------------------------------------------------------------------------------
#	['u2', 8, 'u1', 1, [['sw6-sw5', 11, 12], ['sw5-sw3', 13, 14], ['sw3-sw1', 15, 16]], 'No VLAN U1 with VLAN U2', [80], [801]]
#------------------------------------------------------------------------------------------------------

# u2(8)<->sw6-sw5(11)

    p4.Ingress.no_vlan_traffic_table.add_with_add_u_vlan(
        ingress_port=8,
        new_vid=80,
        egress_port=11
    )

    p4.Egress.egress_s_vlan_traffic_table.add_with_swap_outer_vlan(
        egress_port=11,
        ether_type=0x8100,
        vid=80,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        new_vid=801
    )

# sw6-sw5(12)<->sw5-sw3(13)

    p4.Ingress.vlan_traffic_table.add_with_forward(
        ingress_port=12,
        vid=801,
        ether_type=0x88a8,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        egress_port=13
    )

    p4.Egress.egress_s_vlan_traffic_table.add_with_modify_s_vlan(
        egress_port=13,
        ether_type=0x88a8,
        vid=801,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        new_vid=802
    )

# sw5-sw3(14)<->sw3-sw1(15)

    p4.Ingress.vlan_traffic_table.add_with_forward(
        ingress_port=14,
        vid=802,
        ether_type=0x88a8,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        egress_port=15
    )

    p4.Egress.egress_s_vlan_traffic_table.add_with_modify_s_vlan(
        egress_port=15,
        ether_type=0x88a8,
        vid=802,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        new_vid=803
    )

# sw3-sw1(16)<->u1(1)

    p4.Ingress.vlan_traffic_table.add_with_forward(
        ingress_port=16,
        vid=803,
        ether_type=0x88a8,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        egress_port=1
    )

    p4.Egress.egress_s_vlan_traffic_table.add_with_swap_vlans_rm_int(
        egress_port=1,
        ether_type=0x88a8,
        vid=803,
        vid_mask=0xFF,
        MATCH_PRIORITY=20
    )

#------------------------------------------------------------------------------------------------------
#	['u3', 9, 'u1', 1, [['sw6-sw5', 11, 12], ['sw5-sw3', 13, 14], ['sw3-sw1', 15, 16]], 'VLAN translation', [90], [901]]
#------------------------------------------------------------------------------------------------------

# u3(9)<->sw6-sw5(11)

    p4.Ingress.vlan_traffic_table.add_with_modify_u_vlan(
        ingress_port=9,
        vid=90,
        ether_type=0x8100,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        new_vid=91,
        egress_port=11
    )

    p4.Egress.egress_s_vlan_traffic_table.add_with_swap_outer_vlan(
        egress_port=11,
        ether_type=0x8100,
        vid=91,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        new_vid=901
    )

# sw6-sw5(12)<->sw5-sw3(13)

    p4.Ingress.vlan_traffic_table.add_with_forward(
        ingress_port=12,
        vid=901,
        ether_type=0x88a8,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        egress_port=13
    )

    p4.Egress.egress_s_vlan_traffic_table.add_with_modify_s_vlan(
        egress_port=13,
        ether_type=0x88a8,
        vid=901,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        new_vid=902
    )

# sw5-sw3(14)<->sw3-sw1(15)

    p4.Ingress.vlan_traffic_table.add_with_forward(
        ingress_port=14,
        vid=902,
        ether_type=0x88a8,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        egress_port=15
    )

    p4.Egress.egress_s_vlan_traffic_table.add_with_modify_s_vlan(
        egress_port=15,
        ether_type=0x88a8,
        vid=902,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        new_vid=903
    )

# sw3-sw1(16)<->u1(1)

    p4.Ingress.vlan_traffic_table.add_with_forward(
        ingress_port=16,
        vid=903,
        ether_type=0x88a8,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        egress_port=1
    )

    p4.Egress.egress_s_vlan_traffic_table.add_with_swap_vlans_rm_int(
        egress_port=1,
        ether_type=0x88a8,
        vid=903,
        vid_mask=0xFF,
        MATCH_PRIORITY=20
    )

#------------------------------------------------------------------------------------------------------
#	['u1', 1, 'u4', 10, [['sw1-sw2', 2, 3], ['sw2-sw4', 4, 5], ['sw4-sw6', 6, 7]], 'No VLAN', [100], [1001]]
#------------------------------------------------------------------------------------------------------

# u1(1)<->sw1-sw2(2)

    p4.Ingress.no_vlan_traffic_table.add_with_forward(
        ingress_port=1,
        egress_port=2
    )

    p4.Egress.egress_normal_traffic_table.add_with_add_s_vlan(
        egress_port=2,
        new_vid=1001
    )

# sw1-sw2(3)<->sw2-sw4(4)

    p4.Ingress.vlan_traffic_table.add_with_forward(
        ingress_port=3,
        vid=1001,
        ether_type=0x88a8,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        egress_port=4
    )

    p4.Egress.egress_s_vlan_traffic_table.add_with_modify_s_vlan(
        egress_port=4,
        ether_type=0x88a8,
        vid=1001,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        new_vid=1002
    )

# sw2-sw4(5)<->sw4-sw6(6)

    p4.Ingress.vlan_traffic_table.add_with_forward(
        ingress_port=5,
        vid=1002,
        ether_type=0x88a8,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        egress_port=6
    )

    p4.Egress.egress_s_vlan_traffic_table.add_with_modify_s_vlan(
        egress_port=6,
        ether_type=0x88a8,
        vid=1002,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        new_vid=1003
    )

# sw4-sw6(7)<->u4(10)

    p4.Ingress.vlan_traffic_table.add_with_forward(
        ingress_port=7,
        vid=1003,
        ether_type=0x88a8,
        vid_mask=0xFF,
        MATCH_PRIORITY=20,
        egress_port=10
    )

    p4.Egress.egress_s_vlan_traffic_table.add_with_rm_s_vlan_rm_int(
        egress_port=10,
        ether_type=0x88a8,
        vid=1003,
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