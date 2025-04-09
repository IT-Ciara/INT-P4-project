# F I X  T H I S  L A T E R

import sys
import os
import time
import bfrt_grpc.client as gc
import json
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
import ipaddress

from case_functions import p4_functions as p4f  # No need for relative import
from case_functions import add_entries as ae  # No need for relative import
from case_functions import create_pkts as cp  # No need for relative import
from case_functions import get_counter_stats as gcs  # No need for relative import
from case_functions import sniff_pkts as sp  # No need for relative import

# List of interfaces to sniff
interfaces = ["veth0", "veth2", "veth4", "veth6", "veth8", 
              "veth10","veth12", "veth14", "veth16", "veth18", 
              "veth20", "veth22", "veth24", "veth26", "veth28",
              "veth30", "veth32","veth250"]

def split_128bit_to_32bit_chunks(val):
    return [
        (val >> 96) & 0xFFFFFFFF,
        (val >> 64) & 0xFFFFFFFF,
        (val >> 32) & 0xFFFFFFFF,
        val & 0xFFFFFFFF
    ]

#===============================================================================
#                         C A S E 19: 
#===============================================================================
def main():
    p4f.print_console("blue","Case 19")
    with open('../polka/route_info.json', 'r') as f:
        route_data = json.load(f)    

    ingress_port=1
    egress_port=10
    mirror_port=16

    ing_mir=1 
    ing_ses=150
    egr_mir=0
    egr_ses=0 


    endpoint =1
    core_node=0
    edge_node=1
    selected_node = 2

    #=================Packet details=================
    pkt_override = {
        "ethernet": {
            "valid": True,
            "dst_addr": "aa:aa:aa:aa:aa:aa",
            "src_addr": "bb:bb:bb:bb:bb:bb",
            "ether_type": 0x800
        },
        "polka":{
            "valid":False,
            "proto": 0x0601,
            # "routeid": 0xf
            "routeid": int(route_data['route']['values']['hex_route_id'], 16)
        },
        "outer_vlan": {
            "valid": False,
            "vid": 200,
            "ether_type": 0x800
        },
        "custom_int_shim": {
            "valid": False,
            "ig_tstamp": 0,
            "stack_full": 0,
            "mtu_full": 0,
            "padding": 0,
            "int_count": 2,
            "next_hdr": 0x8100,
            "reserved": 0
        },
        # "inner_vlan": {
        #     "valid": False,
        #     "vid": 0,
        #     "ether_type": 0
        # },
        "ipv4": {
            "valid": True,
            "src_addr": "192.168.233.2",
            "dst_addr": "192.168.233.3",
            "protocol": 17
        },
        # "udp": {
        #     "valid": True,
        #     "src_port": 1000,
        #     "dst_port": 1001
        # },
        # "tcp": {
        #     "valid": False,
        #     "src_port": 1000,
        #     "dst_port": 1001
        # },
        # "raw": {
        #     "valid": True,
        #     "data": "Packet Payload Here"
        # },
        # "lldp": {
        #     "valid": False,
        #     "chassis_id": "00:11:22:33:44:55",
        #     "port_id": "eth0",
        #     "ttl": 120
        # }        
    }

    #===============P4Runtime connection================
    interface, dev_tgt, bfrt_info = p4f.gc_connect()

    #===============Clear tables================
    p4f.clear_all_tables(bfrt_info, dev_tgt)

    #=====================================================
    #=====================Stages==========================
    # ====== Stage 1: User Port? ====== 
    # YES
    stg1_ig_table_name = 'pipe.Ingress.ig_user_port_tbl'
    stg1_ig_actions = ['user_port']
    #===================Add entries=====================
    #---------------------------------------------------
    p4f.print_console("grey","Adding entries to tables",100,'-')
    # Add entries to the tables
    stg1_ig_table = bfrt_info.table_get(stg1_ig_table_name)
    stg1_ig_table.entry_del(dev_tgt,[])
    key = stg1_ig_table.make_key([gc.KeyTuple("ig_intr_md.ingress_port", ingress_port)])
    data = stg1_ig_table.make_data([gc.DataTuple("user_port", 1)],action_name=f"Ingress.{stg1_ig_actions[0]}")
    stg1_ig_table.entry_add(dev_tgt, [key], [data])



    # ====== Stage 2: Has Polka ID? ====== 
    # N/A



    # ====== Stage 3: Topology Discovery? ======
    # N/A



    # ====== Stage 3: Link Continuity Test? ======
    # N/A



    # ====== Stage 4: Partner-Provided Link? ======
    # N/A



    # ====== Stage 5: SDN Trace? ======
    # N/A



    # ====== Stage 6: Contention Flow? ======
    # N/A



    # ====== Stage 7: Port Loop? ======
    # N/A



    # ====== Stage 7: VLAN Loop? ======
    # N/A



    # ====== Stage 8: Flow Mirror? ======
    # N/A



    # ====== Stage 9: Port Mirror? ======
    # YES
    stg_9_ig_tbl_name = "Ingress.ig_port_mirror_tbl"
    stg_9_ig_actions = ['set_md_port_mirror']
  
    #===================Add entries=====================
    stg_9_ig_tbl = bfrt_info.table_get(stg_9_ig_tbl_name)
    stg_9_ig_tbl.entry_del(dev_tgt,[])
    key = stg_9_ig_tbl.make_key([gc.KeyTuple("ig_intr_md.ingress_port", ingress_port)])
    data = stg_9_ig_tbl.make_data([
        gc.DataTuple("egress_port", egress_port),
        gc.DataTuple("ing_mir", ing_mir),
        gc.DataTuple("ing_ses", ing_ses),
        gc.DataTuple("egr_mir", egr_mir),
        gc.DataTuple("egr_ses", egr_ses)
    ],action_name=f"Ingress.{stg_9_ig_actions[0]}")
    stg_9_ig_tbl.entry_add(dev_tgt, [key], [data])
    print("Ingress port mirror entry added successfully.") 




    # ====== Stage 10: No Polka - Destination Endpoint? ======
    # YES
    # ====== Ingress ====
    ig_table_name = "Ingress.ig_no_polka_dst_ep_tbl"
    ig_actions = ['forward','add_u_vlan','modify_u_vlan']
    
    #===================Add entries=====================
    ig_table = bfrt_info.table_get(ig_table_name)
    ig_table.entry_del(dev_tgt,[])
    key = ig_table.make_key([gc.KeyTuple("ig_intr_md.ingress_port", ingress_port),
                             gc.KeyTuple("hdr.ethernet.ether_type",pkt_override['ethernet']['ether_type']),
                             gc.KeyTuple("hdr.outer_vlan.vid", 0,0)
                            #  gc.KeyTuple("hdr.outer_vlan.vid", int(pkt_override['outer_vlan']['vid']),0xFF)
                             ])
    data = ig_table.make_data([gc.DataTuple("egress_port", egress_port),
                               gc.DataTuple("endpoint", endpoint),
                               gc.DataTuple("new_vid",int(pkt_override['outer_vlan']['vid'])),
                               ],
                              action_name=f"Ingress.{ig_actions[1]}") #Forward
    ig_table.entry_add(dev_tgt, [key], [data])



    # ====== Stage 11: Polka - Destination Endpoint? ======  
    # N/A



    #==================================================================
    # ======= P O L K A - R E G I S T E R S ========
    #==================================================================
    # ====== Ingress ====
    # #-------Set the node to core node-------    
    core_node_reg_tbl_name = "Ingress.core_node"
    core_node_table = bfrt_info.table_get(core_node_reg_tbl_name)
    core_node_table.entry_del(dev_tgt,[])

    key = core_node_table.make_key([gc.KeyTuple("$REGISTER_INDEX",0)])
    data = core_node_table.make_data([gc.DataTuple('Ingress.core_node.f1', core_node)])
    core_node_table.entry_mod(dev_tgt, [key], [data])
    
    # ======= Egress ======
    # #-------Set the node to edge node-------
    edne_node_reg_tbl_name = "Egress.edge_node"   
    edge_node_table = bfrt_info.table_get(edne_node_reg_tbl_name)
    edge_node_table.entry_del(dev_tgt,[])

    key = edge_node_table.make_key([gc.KeyTuple("$REGISTER_INDEX",0)])
    data = edge_node_table.make_data([gc.DataTuple('Egress.edge_node.f1', edge_node)])
    edge_node_table.entry_mod(dev_tgt, [key], [data])
    
    # ======== Route ID ========
    # #-------Set the route ID-------
    routeid_int = route_data['route']['values']['int_route_id']
    chunks = split_128bit_to_32bit_chunks(routeid_int)
    reg_names = [
        "Egress.routeId_high_upper",
        "Egress.routeId_high_lower",
        "Egress.routeId_low_upper",
        "Egress.routeId_low_lower"
    ]
    for i, reg_name in enumerate(reg_names):
        routeId_tbl = bfrt_info.table_get(reg_name)
        key = routeId_tbl.make_key([gc.KeyTuple('$REGISTER_INDEX', 0)])
        data = routeId_tbl.make_data([
            gc.DataTuple(f'{reg_name}.f1', chunks[i])
        ])
        routeId_tbl.entry_mod(dev_tgt, [key], [data])
    
    # =========== Node ID ===========
    node_key = f"node_{selected_node}"
    node_id_hex = route_data['nodes'][node_key]['id']['hex_node_id']
    node_id_int = int(node_id_hex, 16) & 0xffff  # Convert then mask    
    algorithm_tbl = bfrt_info.table_get("Ingress.hash.algorithm")
    data_field_list = [
        gc.DataTuple("polynomial",node_id_int), #node_id
    ]
    data_list = algorithm_tbl.make_data(data_field_list,"user_defined")
    algorithm_tbl.default_entry_set(dev_tgt, data_list)  

    #==================================================================  



               
    #===================Sniff packets====================
    #---------------------------------------------------
    print("Starting multi-interface sniffer")
    p4f.print_console("grey","Starting multi-interface sniffer",100,'-')
    ingress_veth = f"veth{ingress_port*2}"
    #Exclude the ingress port from interfaces
    interfaces.remove(ingress_veth)
    sniff_threads,capture_results = sp.start_multi_sniffer_in_background(interfaces, timeout=7)
    # Give sniffers a moment to start up
    time.sleep(3)

    #===================Send packets=====================
    #---------------------------------------------------
    p4f.print_console("reset",f"Sending packets veth{ingress_port*2}",70)
    #replace the ether src 
    
    cp.send_pkts(pkt_override,interface=ingress_port)
    time.sleep(1)

    #=============== Wait for Sniffers to Finish =================
    for thread in sniff_threads:
        thread.join()  # Ensures the sniffers finish before printing stats

    # Check if NO packets were captured on ANY interface
    if not any(capture_results.values()):  
        p4f.print_console("reset", "- - - PACKET CAPTURE RESULTS - - -", 100)
        p4f.print_console("grey", "No packets captured on any interface", 100, '-', space=False)    

    #===========Disconnect Interface================
    interface.tear_down_stream()



if __name__ == "__main__":
    main()    