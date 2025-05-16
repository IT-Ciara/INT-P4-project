import os
import ipaddress
import random
import csv
import os
import ipaddress
import random
import csv
import struct
import socket
import sys
import time
import bfrt_grpc.client as gc
import bfrt_grpc.bfruntime_pb2 as bfruntime_pb2
import p4_functions as p4f


def add_mirror_cfg_entry(mirror_cfg_table, dev_tgt):
    key = mirror_cfg_table.make_key([gc.KeyTuple('$sid', 200)])
    data = mirror_cfg_table.make_data([
        gc.DataTuple('$direction', str_val="INGRESS"),
        gc.DataTuple('$session_enable', bool_val=True),
        gc.DataTuple('$ucast_egress_port', 15),
        gc.DataTuple('$ucast_egress_port_valid', bool_val=True),
    ], "$normal")
    mirror_cfg_table.entry_add(dev_tgt, [key], [data])


def add_entry(table, dev_tgt, ingress_port, vid, proto, dst_port, 
              egress_port, ing_mir, ing_ses, egr_mir, egr_ses):
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
                            action_name="Ingress.ig_stg_6.set_md")
    table.entry_add(dev_tgt, [key], [data])

    

def main():
    interface, dev_tgt, bfrt_info = p4f.gc_connect()
    table_name= 'pipe.Ingress.ig_stg_6.ig_flow_mirror_tbl'
    table = p4f.get_table_info(table_name, bfrt_info)
    p4f.clear_table(table, dev_tgt)

    mirror_cfg_table = '$mirror.cfg'
    mirror_cfg_table = bfrt_info.table_get(mirror_cfg_table)
    p4f.clear_table(mirror_cfg_table, dev_tgt)
    
    add_mirror_cfg_entry(mirror_cfg_table, dev_tgt)
    add_entry(table, dev_tgt,ingress_port=6, vid=1000, proto=17, dst_port=55, 
              egress_port=8, ing_mir=1, ing_ses=40, egr_mir=0, egr_ses=0)
    # # Cleanup
    interface.tear_down_stream()  
    
if __name__ == "__main__":
    main()
