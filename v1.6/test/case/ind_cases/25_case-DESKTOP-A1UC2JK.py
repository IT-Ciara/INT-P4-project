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
# interfaces = ["veth0", "veth2", "veth4", "veth6", "veth8", 
#               "veth10","veth12", "veth14", "veth16", "veth18", 
#               "veth20", "veth22", "veth24", "veth26", "veth28",
#               "veth30", "veth32","veth250"]
# List of interfaces to sniff
# interfaces = ["enp4s0f0","enp4s0f1"]

import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Run P4 test case with specified target")
parser.add_argument("--target", required=True, help="Target model to use (e.g., tf2_model)")
args = parser.parse_args()

# Resolve directory paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Load ports configuration for the specified target
TARGET = args.target

with open(f'./ports/{TARGET}.json', 'r') as f:
    ports_data = json.load(f)  



interfaces = ports_data['interfaces']

def split_128bit_to_32bit_chunks(val):
    return [
        (val >> 96) & 0xFFFFFFFF,
        (val >> 64) & 0xFFFFFFFF,
        (val >> 32) & 0xFFFFFFFF,
        val & 0xFFFFFFFF
    ]


def ig_set_port_md(ig_port_info_tbl,dev_tgt,ingress_port,ig_user_port,egress_port,action):
    #Add entries to the table
    key =ig_port_info_tbl.make_key([gc.KeyTuple("ig_intr_md.ingress_port",ingress_port)])
    data =ig_port_info_tbl.make_data([gc.DataTuple("user_port",ig_user_port),

                                        gc.DataTuple("egress_port",egress_port)],
                                        action_name=f"Ingress.{action}")
    ig_port_info_tbl.entry_add(dev_tgt, [key], [data])

def eg_set_port_md(eg_edge_port_tbl,dev_tgt,egress_port,eg_user_port,eg_p4_sw_port,eg_transit_port,action):
    key=eg_edge_port_tbl.make_key([gc.KeyTuple("eg_intr_md.egress_port",egress_port)])
    data=eg_edge_port_tbl.make_data([gc.DataTuple("user_port",eg_user_port),
                                      gc.DataTuple("p4_sw_port",eg_p4_sw_port),
                                      gc.DataTuple("transit_port",eg_transit_port)],
                                      action_name=f"Egress.{action}")
    eg_edge_port_tbl.entry_add(dev_tgt, [key], [data])


def egress_user_port_tbl(eg_user_port_tbl,dev_tgt,ether_type,u_vid,u_mask,s_vid,s_mask,action,new_vid_actions,new_vid=0):
    if action in new_vid_actions:
        if 'modify' in action:
            new_vid+=50

    if action != 'nothing':
        #Add entries to the table
        key=eg_user_port_tbl.make_key([gc.KeyTuple("hdr.ethernet.ether_type",ether_type),
                                    gc.KeyTuple("hdr.u_vlan.vid",u_vid,u_mask),
                                    gc.KeyTuple("hdr.s_vlan.vid",s_vid,s_mask),
                                    ])
        if new_vid != 0:
            data =eg_user_port_tbl.make_data([gc.DataTuple("new_vid",new_vid)],
                                        action_name=f"Egress.{action}")
        else:   
            data =eg_user_port_tbl.make_data([],
                                        action_name=f"Egress.{action}")
        eg_user_port_tbl.entry_add(dev_tgt, [key], [data])

def egress_p4_sw_port_tbl(eg_p4_sw_port_tbl,dev_tgt,ether_type,eg_p4_sw_port,action,ig_ingress_port):
    if action != 'nothing':
        #Add entries to the table
        key=eg_p4_sw_port_tbl.make_key([gc.KeyTuple("hdr.ethernet.ether_type",ether_type),
                                        gc.KeyTuple("hdr.ig_metadata.ig_port",ig_ingress_port),
                                        gc.KeyTuple("meta.p4_sw_port",eg_p4_sw_port),
                                        ])
        data =eg_p4_sw_port_tbl.make_data([],
                                            action_name=f"Egress.{action}")
        eg_p4_sw_port_tbl.entry_add(dev_tgt, [key], [data])

def egress_transit_port_tbl(eg_transit_port_tbl,dev_tgt,ether_type,eg_transit_port,action,ig_ingress_port,s_vid=900):
    if action != 'nothing':
        #Add entries to the table
        key=eg_transit_port_tbl.make_key([gc.KeyTuple("hdr.ethernet.ether_type",ether_type),
                                          gc.KeyTuple("hdr.ig_metadata.ig_port",ig_ingress_port),
                                        gc.KeyTuple("meta.transit_port",eg_transit_port),
                                        ])
        data =eg_transit_port_tbl.make_data([gc.DataTuple("new_vid",s_vid)],
                                            action_name=f"Egress.{action}")
        eg_transit_port_tbl.entry_add(dev_tgt, [key], [data])


#===============================================================================
#                         C A S E 25: 
#===============================================================================
def main():
    p4f.print_console("blue","Case 25")
    with open(f'../polka/route_info_{TARGET}.json', 'r') as f:
        route_data = json.load(f)    

    initial_ingress_port = interfaces[1]
    selected_node = 1

    ing_mir=1 
    ing_ses=55
    egr_mir=0
    egr_ses=0 


    ports_config = {
        "1": {
            # "ingress_port": 64,
            "ingress_port": ports_data['ingress_port'],
            "ingress_port_md": [0,1,0,0],
            # "egress_port":66,
            "egress_port": ports_data['egress_port'],
            "egress_port_md": [0,1,0],
            #eth type, u_vlan, u_vlan mask, s_vlan, s_vlan mask
            "pkt_values": [0x8842,0,0x0,0,0x0],
            "action": "nothing"
        }
    }



    #=================Packet details=================
    pkt_override = {
        "ethernet": {
            "valid": True,
            "dst_addr": "aa:aa:aa:aa:aa:aa",
            "src_addr": "bb:bb:bb:bb:bb:bb",
            "ether_type": 0x8842
        },
        "s_vlan": {
            "valid":False,
            "vid": 900,
            "ether_type": 0x8100
        }, 
        "polka":{
            "valid":True,
            "proto": 0x0601,
            "routeid": int(route_data['route']['values']['hex_route_id'], 16)
        },        
        "custom_int_shim": {
            "valid": True,
            "int_count": 1,
            "next_hdr": 0x800,
        },          
        "u_vlan": {
            "valid": False,
            "vid": 200,
            "ether_type": 0x800
        },
        "ipv4": {
            "valid": True,
            "src_addr": "192.168.233.2",
            "dst_addr": "192.168.233.3",
            "protocol": 17
        }    
    }

    #===============P4Runtime connection================
    interface, dev_tgt, bfrt_info = p4f.gc_connect()

    #===============Clear tables================
    p4f.clear_all_tables(bfrt_info, dev_tgt)

    #---------------------------------------------------------------------------------------------------------------------------
    #================================================== T A B L E S ============================================================
    #---------------------------------------------------------------------------------------------------------------------------


    #============================================ I N G R E S S    T A B L E S =================================================
    #---------------------------------------------------------------------------------------------------------------------------
    
    #============================================ I N G R E S S    T A B L E S =================================================
    #---------------------------------------------------------------------------------------------------------------------------
    ig_port_info_tbl_name = 'pipe.Ingress.ig_port_info_tbl'
    ig_port_info_tbl_actions = ['set_port_md']
    ig_action = ig_port_info_tbl_actions[0]
    #---------------------------------------------------
    ig_port_info_tbl = bfrt_info.table_get(ig_port_info_tbl_name)
    ig_port_info_tbl.entry_del(dev_tgt,[])

    #=====================================================
    #=====================Stages==========================
    # ====== Stage 1: User Port? ====== 
    # N/A



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
    # N/A




    # ====== Stage 10: No Polka - Destination Endpoint? ======
    # N/A



    # ====== Stage 11: Polka - Destination Endpoint? ======  
    # N/A




















    #============================================== E G R E S S    T A B L E S =================================================
    #---------------------------------------------------------------------------------------------------------------------------

    #=====================================================
    #=====================Stages==========================
    # ====== Stage 1: User Port? ====== 
    # N/A



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
    # N/A




    # ====== Stage 10: No Polka - Destination Endpoint? ======
    # N/A



    # ====== Stage 11: Polka - Destination Endpoint? ======  
    # N/A




    #============================================== E G R E S S    T A B L E S =================================================
    #---------------------------------------------------------------------------------------------------------------------------

    #============= EGRESS PORT TABLE ===============
    #-----------------------------------------------
    eg_port_info_tbl_name = 'pipe.Egress.eg_port_info_tbl'
    eg_port_info_tbl_actions = ['set_port_md']
    eg_action = eg_port_info_tbl_actions[0]
    #---------------------------------------------------
    eg_edge_port_tbl = bfrt_info.table_get(eg_port_info_tbl_name)
    eg_edge_port_tbl.entry_del(dev_tgt,[])

    #============= EGRESS USER PORT TABLE ===============
    #----------------------------------------------------
    eg_user_port_tbl_name = 'pipe.Egress.eg_user_port_tbl'
    eg_user_port_tbl_actions = ['add_u_vlan', 'modify_u_vlan', #0 #1
                                'remove_u_vlan', 'rm_s_vlan', #2 #3
                                'rm_s_vlan_modify_u_vlan', 'rm_s_vlan_u_vlan', #4 #5
                                'rm_s_vlan_add_u_vlan', 'rm_polka_int', #6 #7
                                'rm_polka_int_modify_u_vlan', 'rm_polka_int_u_vlan', #8 #9
                                'rm_polka_int_add_u_vlan','nothing'] #10 #11
    new_vid_actions = ['add_u_vlan', 'modify_u_vlan', 'rm_s_vlan_modify_u_vlan', 'rm_s_vlan_add_u_vlan', 'rm_polka_int_modify_u_vlan', 'rm_polka_int_add_u_vlan']
    #---------------------------------------------------
    eg_user_port_tbl = bfrt_info.table_get(eg_user_port_tbl_name)
    eg_user_port_tbl.entry_del(dev_tgt,[])

    #============= EGRESS P4 SW PORT TABLE ===============
    #----------------------------------------------------   
    eg_p4_sw_port_tbl_name = 'pipe.Egress.eg_p4_sw_port_tbl'
    eg_p4_sw_port_tbl_actions = ['add_int_polka', 'rm_s_vlan_add_int_polka', 'rm_md']
    #---------------------------------------------------
    eg_p4_sw_port_tbl = bfrt_info.table_get(eg_p4_sw_port_tbl_name)
    eg_p4_sw_port_tbl.entry_del(dev_tgt,[])

    #============= EGRESS TRANSIT PORT TABLE ===============
    #-------------------------------------------------------
    eg_transit_port_tbl_name = 'pipe.Egress.eg_transit_port_tbl'
    eg_transit_port_tbl_actions = ['add_s_vlan_rm_int_polka','add_s_vlan','rm_md']
    #---------------------------------------------------
    eg_transit_port_tbl = bfrt_info.table_get(eg_transit_port_tbl_name)
    eg_transit_port_tbl.entry_del(dev_tgt,[])





    #=================Add entries to tables=================
    #---------------------------------------------------
    #Add entries to the ingress port table
    p4f.print_console("grey","Adding entries to the ingress port table",100,'-')

    #Iterate through the ports_config dictionary
    for port, config in ports_config.items():
        ingress_port = config['ingress_port']
        ig_user_port = config['ingress_port_md'][0]
        egress_port = config['egress_port']
        eg_user_port, eg_p4_sw_port, eg_transit_port = config['egress_port_md']
        print(f"Ingress port: {ingress_port}")
        print(f"Ig User Port: {ig_user_port}")
        print(f"Egress port: {egress_port}")
        print(f"Eg User Port: {eg_user_port}, Eg P4 SW Port: {eg_p4_sw_port}, Eg Transit Port: {eg_transit_port}")

        eth_type, u_vid, u_mask, s_vid, s_mask = config['pkt_values']
        print(f"Packet values: Eth Type: {hex(eth_type)}, U VID: {u_vid}, U Mask: {u_mask}, S VID: {s_vid}, S Mask: {s_mask}")


        #Add entries to the ingress port table
        ig_set_port_md(ig_port_info_tbl,dev_tgt,ingress_port,ig_user_port,egress_port,'set_port_md')

        #Add entries to the egress port table
        eg_set_port_md(eg_edge_port_tbl,dev_tgt,egress_port,eg_user_port,eg_p4_sw_port,eg_transit_port,'set_port_md')

        eg_action = config['action']
        print(f"Action: {eg_action}")
        if eg_user_port==1:
            #Add entries to the egress user port table
            egress_user_port_tbl(eg_user_port_tbl,dev_tgt,eth_type,u_vid,u_mask,s_vid,s_mask,eg_action,new_vid_actions)
        elif eg_p4_sw_port==1:
            #Add entries to the egress p4 sw port table
            egress_p4_sw_port_tbl(eg_p4_sw_port_tbl,dev_tgt,eth_type,eg_p4_sw_port,eg_action,ingress_port)
        elif eg_transit_port==1:
            #Add entries to the egress transit port table
            egress_transit_port_tbl(eg_transit_port_tbl,dev_tgt,eth_type,eg_transit_port,eg_action,ingress_port)




        





    #==================================================================
    # ======= P O L K A - R E G I S T E R S ========
    #==================================================================
    
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
    ingress_veth = f"{initial_ingress_port}"
    #Exclude the ingress port from interfaces
    interfaces.remove(ingress_veth)
    sniff_threads,capture_results = sp.start_multi_sniffer_in_background(interfaces, timeout=7)
    # Give sniffers a moment to start up
    time.sleep(3)

    #===================Send packets=====================
    #---------------------------------------------------
    p4f.print_console("reset",f"Sending packets {initial_ingress_port}",70)
    #replace the ether src 
    
    cp.send_pkts(pkt_override,interface=initial_ingress_port)
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