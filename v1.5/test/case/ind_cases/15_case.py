# F I X  T H I S  L A T E R

import sys
import os
import time
import bfrt_grpc.client as gc
import json
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

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
#                         C A S E: 15
#===============================================================================
def main():
    p4f.print_console("blue","Case 15")
    with open('../polka/route_info.json', 'r') as f:
        route_data = json.load(f)    

    ingress_port = 1
    egress_port = 13
    mirror_port = 16
    endpoint =1
    core_node=0
    edge_node=1
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
        # "ipv4": {
        #     "valid": True,
        #     "src_addr": "192.168.230.2",
        #     "dst_addr": "192.168.230.3",
        #     "protocol": 17
        # },
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
    # NO

    # ====== Stage 6: Contention Flow? ======
    # NO

    # ====== Stage 7: Port Loop? ======
    # NO

    # ====== Stage 7: VLAN Loop? ======
    # NO

    # ====== Stage 8: Flow Mirror? ======
    # Yes
    stg_8_ig_tbl_name = "Ingress.ig_flow_mirror_tbl"
    stg_8_ig_actions = ['set_md_flow_mirror']

    #===================Add entries=====================
    #---------------------------------------------------
    stg_8_ig_tbl = bfrt_info.table_get(stg_8_ig_tbl_name)
    stg_8_ig_tbl.entry_del(dev_tgt,[])

    key = stg_8_ig_tbl.make_key([gc.KeyTuple("ig_intr_md.ingress_port", ingress_port)])
    ing_mir = 1 
    ing_ses = 100
    egr_mir = 0
    egr_ses =0

    data = stg_8_ig_tbl.make_data([
        gc.DataTuple("egress_port", egress_port),
        gc.DataTuple("ing_mir", ing_mir),
        gc.DataTuple("ing_ses", ing_ses),
        gc.DataTuple("egr_mir", egr_mir),
        gc.DataTuple("egr_ses", egr_ses)
    ],action_name=f"Ingress.{stg_8_ig_actions[0]}")
    stg_8_ig_tbl.entry_add(dev_tgt, [key], [data])
    print("Ingress port mirror entry added successfully.")    

    # ====== Stage 9: Port Mirror? ======
    # NO

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
                            
  #=============================P O L K A=========================
    #---------------------------------------------------------------
    # ====== Ingress ====
    #=================Set to core node=================
    core_node_reg_tbl_name = "Ingress.core_node"
    edge_node_table = bfrt_info.table_get(core_node_reg_tbl_name)
    edge_node_table.entry_del(dev_tgt,[])

    key = edge_node_table.make_key([gc.KeyTuple('$REGISTER_INDEX', 0)])
    data = edge_node_table.make_data([gc.DataTuple('Ingress.core_node.f1', core_node)])
    edge_node_table.entry_mod(dev_tgt, [key], [data])
    print("Register updated successfully.")

    #===================Add Route ID entries=====================
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
        print(f"Wrote {hex(chunks[i])} to {reg_name} at index 0")

    print("Both 128-bit register values updated successfully.")

    # ======= Egress ======
    # #-------Set the node to edge node-------
    edne_node_reg_tbl_name = "Egress.edge_node"
    edge_node_table = bfrt_info.table_get(edne_node_reg_tbl_name)
    edge_node_table.entry_del(dev_tgt,[])

    key = edge_node_table.make_key([gc.KeyTuple('$REGISTER_INDEX', 0)])
    data = edge_node_table.make_data([gc.DataTuple('Egress.edge_node.f1', edge_node)])
    edge_node_table.entry_mod(dev_tgt, [key], [data])
    print("Register updated successfully.")

    # ====== Stage 11: Polka - Destination Endpoint? ======
    # # N/A
               
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