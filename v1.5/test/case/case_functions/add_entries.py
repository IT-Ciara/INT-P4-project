import sys
import os
import sys
import time
import bfrt_grpc.client as gc
import bfrt_grpc.bfruntime_pb2 as bfruntime_pb2
import struct
import socket
from case_functions import p4_functions as p4f

# S T A G E   2
def add_entry_ingress_port_tbl(dev_tgt, bfrt_info,ingress_port,user_port,action_name,clear_table=False):
    table_name = 'pipe.Ingress.ingress_port_tbl'
    table = p4f.get_table_info(table_name, bfrt_info)
    if clear_table:
        p4f.clear_table(table, dev_tgt)
    key = table.make_key([gc.KeyTuple('ig_intr_md.ingress_port', ingress_port)])
    data = table.make_data([gc.DataTuple('user_port', user_port)], action_name=f"Ingress.{action_name}")
    table.entry_add(dev_tgt, [key], [data])
    
# S T A G E   3
def add_entry_is_sdn_trace_tbl(dev_tgt, bfrt_info,ethernet_src,action_name,clear_table=False):
    table_name = 'pipe.Ingress.is_sdn_trace_tbl'
    table = p4f.get_table_info(table_name, bfrt_info)
    if clear_table:
        p4f.clear_table(table, dev_tgt)
    key = table.make_key([gc.KeyTuple('hdr.ethernet.src_addr', p4f.mac_to_int(ethernet_src))])
    data = table.make_data([], action_name=f"Ingress.{action_name}")
    table.entry_add(dev_tgt, [key], [data])

# S T A G E   4
def add_entry_contention_flow_tbl(dev_tgt, bfrt_info,ingress_port,eth_dst,eth_type,
                                  vlan_id,ipv4_src,ipv4_dst,action_name,clear_table=False):
    table_name = 'pipe.Ingress.contention_flow_tbl'
    table = p4f.get_table_info(table_name, bfrt_info)
    if clear_table:
        p4f.clear_table(table, dev_tgt)
    key = table.make_key([gc.KeyTuple('ig_intr_md.ingress_port', ingress_port),
                          gc.KeyTuple('hdr.ethernet.dst_addr', p4f.mac_to_int(eth_dst)),
                          gc.KeyTuple('hdr.ethernet.ether_type', p4f.mac_to_int(eth_type)),
                        gc.KeyTuple('hdr.outer_vlan.vid', vlan_id),
                        gc.KeyTuple('hdr.ipv4.src_addr', p4f.ip_to_int(ipv4_src)),
                        gc.KeyTuple('hdr.ipv4.dst_addr', p4f.ip_to_int(ipv4_dst))])
    data = table.make_data([], action_name=f"Ingress.{action_name}")
    table.entry_add(dev_tgt, [key], [data])

# S T A G E   5
def add_entry_ig_port_loop_tbl(dev_tgt, bfrt_info,ingress_port,action_name,clear_table=False):
    table_name = 'pipe.Ingress.ig_port_loop_tbl'
    table = p4f.get_table_info(table_name, bfrt_info)
    if clear_table:
        p4f.clear_table(table, dev_tgt)
    key = table.make_key([gc.KeyTuple('ig_intr_md.ingress_port', ingress_port)])
    data = table.make_data([], action_name=f"Ingress.{action_name}")
    table.entry_add(dev_tgt, [key], [data])


def add_entry_ig_vlan_loop_tbl(dev_tgt, bfrt_info,ingress_port,vlan_id,clear_table=False):
    table_name = 'pipe.Ingress.ig_vlan_loop_tbl'
    table = p4f.get_table_info(table_name, bfrt_info)
    if clear_table:
        p4f.clear_table(table, dev_tgt)
    key = table.make_key([gc.KeyTuple('ig_intr_md.ingress_port', ingress_port),gc.KeyTuple('hdr.outer_vlan.vid', vlan_id)])
    data = table.make_data([], action_name=f"Ingress.send_back_vlan")
    table.entry_add(dev_tgt, [key], [data])

# S T A G E   6
def add_entry_ingress_mirror_cfg(dev_tgt, bfrt_info,mirror_port,s_id,clear_table=False):
    mirror_cfg_table = bfrt_info.table_get('$mirror.cfg')
    # entries = p4f.get_all_entries('$mirror.cfg', dev_tgt, bfrt_info)
    #Clear table
    if clear_table:
        mirror_cfg_table.entry_del(dev_tgt)
    key = mirror_cfg_table.make_key([gc.KeyTuple('$sid', s_id)])
    data = mirror_cfg_table.make_data([
        gc.DataTuple('$direction', str_val="INGRESS"),
        gc.DataTuple('$session_enable', bool_val=True),
        gc.DataTuple('$ucast_egress_port', mirror_port),
        gc.DataTuple('$ucast_egress_port_valid', bool_val=True),
    ], "$normal")
    mirror_cfg_table.entry_add(dev_tgt, [key], [data])


def add_entry_ig_flow_mirror_tbl(dev_tgt, bfrt_info,ingress_port,vid,proto,dst_port,
                                 egress_port,ing_mir,ing_ses,egr_mir,egr_ses,mirror_port,clear_table=False):
    table_name = 'pipe.Ingress.ig_flow_mirror_tbl'
    table = p4f.get_table_info(table_name, bfrt_info)
    # if ing_mir ==1:
        # add_entry_ingress_mirror_cfg(dev_tgt,bfrt_info, mirror_port,ing_ses,clear_table=True)
    if clear_table:
        p4f.clear_table(table, dev_tgt)
    key = table.make_key([gc.KeyTuple('ig_intr_md.ingress_port', ingress_port),
                          gc.KeyTuple('hdr.outer_vlan.vid', vid),
                          gc.KeyTuple('hdr.ipv4.protocol', proto),
                          gc.KeyTuple('meta.l4_dst_port', dst_port)])
    data = table.make_data([gc.DataTuple('egress_port', egress_port),
                        gc.DataTuple('ing_mir', ing_mir),
                        gc.DataTuple('ing_ses', ing_ses), 
                        gc.DataTuple('egr_mir', egr_mir), 
                        gc.DataTuple('egr_ses', egr_ses)
                        ],
                        action_name=f"Ingress.set_md_flow_mirror")
    table.entry_add(dev_tgt, [key], [data])

# S T A G E  7
def add_entry_ig_polka_type_tbl(dev_tgt, bfrt_info, ether_type, action, clear_table=False):
    table_name = 'pipe.Ingress.ig_polka_type_tbl'
    table = p4f.get_table_info(table_name, bfrt_info)
    if clear_table:
        p4f.clear_table(table, dev_tgt)
    key = table.make_key([gc.KeyTuple('hdr.ethernet.ether_type', p4f.mac_to_int(ether_type))])
    data = table.make_data([], action_name=f"Ingress.{action}")
    table.entry_add(dev_tgt, [key], [data])



# S T A G E  8
def add_entry_ig_topolog_discovery_tbl(dev_tgt, bfrt_info,ingress_port,ether_type,action,clear_table=False):
    table_name = 'pipe.Ingress.ig_topolog_discovery_tbl'
    table = p4f.get_table_info(table_name, bfrt_info)
    if clear_table:
        p4f.clear_table(table, dev_tgt)
    key = table.make_key([gc.KeyTuple('ig_intr_md.ingress_port', ingress_port),
                          gc.KeyTuple('hdr.ethernet.ether_type', p4f.mac_to_int(ether_type))])
    data = table.make_data([], action_name=f"Ingress.{action}")
    table.entry_add(dev_tgt, [key], [data])


def add_entry_ig_link_continuity_test_tbl(dev_tgt, bfrt_info,ingress_port,ether_type,action,clear_table=False):
    table_name = 'pipe.Ingress.ig_link_continuity_test_tbl'
    table = p4f.get_table_info(table_name, bfrt_info)
    if clear_table:
        p4f.clear_table(table, dev_tgt)
    key = table.make_key([gc.KeyTuple('ig_intr_md.ingress_port', ingress_port),
                          gc.KeyTuple('hdr.ethernet.ether_type', p4f.mac_to_int(ether_type))])
    data = table.make_data([], action_name=f"Ingress.{action}")
    table.entry_add(dev_tgt, [key], [data])

# S T A G E  9
def add_entry_ig_partner_provided_link_tbl(dev_tgt, bfrt_info,ingress_port,
                                           vlan_id,eh_type,action,clear_table=False):
    table_name = 'pipe.Ingress.ig_partner_provided_link_tbl'
    table = p4f.get_table_info(table_name, bfrt_info)
    if clear_table:
        p4f.clear_table(table, dev_tgt)
    key = table.make_key([gc.KeyTuple('ig_intr_md.ingress_port', ingress_port),
                          gc.KeyTuple('hdr.outer_vlan.vid', vlan_id),
                          gc.KeyTuple('hdr.ethernet.ether_type', p4f.mac_to_int(eh_type))])
    data = table.make_data([], action_name=f"Ingress.{action}")
    table.entry_add(dev_tgt, [key], [data])
    
def add_entry_eg_int_tbl(dev_tgt, bfrt_info,rm_s_vlan,add_int,
                         new_vid=0,
                         add_int_after_vlan=0,
                         add_s_vlan=0,
                         action="set_rm_s_vlan_add_int",
                         clear_table=False):
    table_name = 'pipe.Egress.eg_int_tbl'
    table = p4f.get_table_info(table_name, bfrt_info)
    if clear_table:
        p4f.clear_table(table, dev_tgt)

    if action == "add_int_after_vlan":
        key = table.make_key([gc.KeyTuple('hdr.ig_metadata.rm_s_vlan', rm_s_vlan),
                            gc.KeyTuple('hdr.ig_metadata.add_int', add_int),
                            gc.KeyTuple('hdr.ig_metadata.add_int_after_vlan', 1),
                            gc.KeyTuple('hdr.ig_metadata.add_s_vlan', 0)])
        data = table.make_data([], action_name=f"Egress.{action}")
        table.entry_add(dev_tgt, [key], [data])

    elif action == "add_s_vlan":
        key = table.make_key([gc.KeyTuple('hdr.ig_metadata.rm_s_vlan', rm_s_vlan),
                            gc.KeyTuple('hdr.ig_metadata.add_int', add_int),
                            gc.KeyTuple('hdr.ig_metadata.add_int_after_vlan', 0),
                            gc.KeyTuple('hdr.ig_metadata.add_s_vlan', 1)])
        data = table.make_data([gc.DataTuple('new_vid', new_vid)], action_name=f"Egress.{action}")
        table.entry_add(dev_tgt, [key], [data])

    elif action == "set_rm_s_vlan_add_int":
        key = table.make_key([gc.KeyTuple('hdr.ig_metadata.rm_s_vlan', rm_s_vlan),
                            gc.KeyTuple('hdr.ig_metadata.add_int', add_int),
                            gc.KeyTuple('hdr.ig_metadata.add_int_after_vlan', 0),
                            gc.KeyTuple('hdr.ig_metadata.add_s_vlan', 0)])
        data = table.make_data([], action_name=f"Egress.{action}")
        table.entry_add(dev_tgt, [key], [data])






# S T A G E  10
def add_entry_mirror_cfg(dev_tgt, bfrt_info,egress_port,ig_sess,eg_sess,clear_table=False):
    mirror_cfg_table = bfrt_info.table_get('$mirror.cfg')
    entries = p4f.get_all_entries('$mirror.cfg', dev_tgt, bfrt_info)
    #Clear table
    if clear_table:
        mirror_cfg_table.entry_del(dev_tgt)
    if ig_sess>0:
        key = mirror_cfg_table.make_key([gc.KeyTuple('$sid', ig_sess)])
        data = mirror_cfg_table.make_data([
            gc.DataTuple('$direction', str_val="INGRESS"),
            gc.DataTuple('$session_enable', bool_val=True),
            gc.DataTuple('$ucast_egress_port', egress_port),
            gc.DataTuple('$ucast_egress_port_valid', bool_val=True),
        ], "$normal")
    elif eg_sess>0:
        key = mirror_cfg_table.make_key([gc.KeyTuple('$sid', eg_sess)])
        data = mirror_cfg_table.make_data([
            gc.DataTuple('$direction', str_val="EGRESS"),
            gc.DataTuple('$session_enable', bool_val=True),
            gc.DataTuple('$ucast_egress_port', egress_port),
            gc.DataTuple('$ucast_egress_port_valid', bool_val=True),
        ], "$normal")
    mirror_cfg_table.entry_add(dev_tgt, [key], [data])



def add_entry_ig_port_mirror_tbl(dev_tgt, bfrt_info,ingress_port,
                                 egress_port,ing_mir,ing_ses,egr_mir,egr_ses,mirror_port,action="set_md_port_mirror",clear_table=False):
    table_name = 'pipe.Ingress.ig_port_mirror_tbl'
    table = p4f.get_table_info(table_name, bfrt_info)
    # if egr_mir == 1 or ing_mir == 1:
        # add_mirror_sessions(dev_tgt, bfrt_info,clear_table=True)
        # add_entry_mirror_cfg(dev_tgt,bfrt_info, mirror_port,ing_ses,egr_ses,clear_table=True)
    if clear_table:
        p4f.clear_table(table, dev_tgt)
    key = table.make_key([gc.KeyTuple('ig_intr_md.ingress_port', ingress_port)])
    data = table.make_data([gc.DataTuple('egress_port', egress_port),
                        gc.DataTuple('ing_mir', ing_mir),
                        gc.DataTuple('ing_ses', ing_ses), 
                        gc.DataTuple('egr_mir', egr_mir), 
                        gc.DataTuple('egr_ses', egr_ses)
                        ],
                        action_name=f"Ingress.{action}")
    table.entry_add(dev_tgt, [key], [data])



# S T A G E  11
def add_entry_ig_end_point_tbl(dev_tgt, bfrt_info, 
                                ingress_port,ether_type,vid,vid_mask,
                                egress_port,
                                PRIORITY=1, 
                                new_vid=0,
                                add_int_after_vlan=0,
                                add_s_vlan=0,
                                action="forward",clear_table=False):
    table_name = 'pipe.Ingress.ig_end_point_tbl'
    table = p4f.get_table_info(table_name, bfrt_info)
    if clear_table:
        p4f.clear_table(table, dev_tgt)
    if action == "forward":
        key = table.make_key([
                                gc.KeyTuple('ig_intr_md.ingress_port', ingress_port),
                                gc.KeyTuple('hdr.ethernet.ether_type', p4f.mac_to_int(ether_type)),
                                gc.KeyTuple('hdr.outer_vlan.vid', int(vid), vid_mask),
                                gc.KeyTuple('$MATCH_PRIORITY', PRIORITY)
                            ])
        data = table.make_data([gc.DataTuple('egress_port', egress_port),
                                gc.DataTuple('add_int_after_vlan', add_int_after_vlan),
                                gc.DataTuple('add_s_vlan', add_s_vlan)
                                ], action_name=f"Ingress.{action}")
    elif action == "add_u_vlan":
        key = table.make_key([gc.KeyTuple('ig_intr_md.ingress_port', ingress_port),
                              gc.KeyTuple('hdr.ethernet.ether_type', p4f.mac_to_int(ether_type)),
                              gc.KeyTuple('hdr.outer_vlan.vid', int(vid), vid_mask),
                              gc.KeyTuple('$MATCH_PRIORITY',  1)
                              ])
        data = table.make_data([gc.DataTuple('egress_port', egress_port),
                                gc.DataTuple('new_vid', int(new_vid)),
                                gc.DataTuple('add_int_after_vlan', add_int_after_vlan),
                                gc.DataTuple('add_s_vlan', add_s_vlan)                                             
                                ], action_name=f"Ingress.{action}")
    elif action == "modify_u_vlan":
        key = table.make_key([gc.KeyTuple('ig_intr_md.ingress_port', ingress_port),
                              gc.KeyTuple('hdr.ethernet.ether_type', p4f.mac_to_int(ether_type)),
                              gc.KeyTuple('hdr.outer_vlan.vid', int(vid), vid_mask),
                              gc.KeyTuple('$MATCH_PRIORITY',  1)
                              ])
        data = table.make_data([gc.DataTuple('egress_port', egress_port),
                                gc.DataTuple('new_vid', int(new_vid)),
                                gc.DataTuple('add_int_after_vlan', add_int_after_vlan),
                                gc.DataTuple('add_s_vlan', add_s_vlan)            
                                ], action_name=f"Ingress.{action}")

    table.entry_add(dev_tgt, [key], [data])
    


                                
                                


