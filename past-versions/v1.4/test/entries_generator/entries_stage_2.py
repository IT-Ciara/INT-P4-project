import sys
import os
import sys
import time
import bfrt_grpc.client as gc
import bfrt_grpc.bfruntime_pb2 as bfruntime_pb2
import struct
import socket
import p4_functions as p4f

def add_entries(table,dev_tgt):
    print(f"CREATE ENTRIES IN {table}")
    user_port = 0
    for i in range(0,16):
        if i >= 0 and i < 8 :
            user_port = 1
        else:
            user_port = 0
        key = table.make_key([gc.KeyTuple('ig_intr_md.ingress_port', i)])
        data = table.make_data([gc.DataTuple('user_port', user_port)], action_name="Ingress.ig_stg_2.user_port")
        table.entry_add(dev_tgt, [key], [data])


def main():
    interface, dev_tgt, bfrt_info = p4f.gc_connect()
    table_name = 'pipe.Ingress.ig_stg_2.ingress_port_tbl'
    table = p4f.get_table_info(table_name, bfrt_info)
    p4f.clear_table(table, dev_tgt)
    
    # Add entries 
    add_entries(table,dev_tgt)
    interface.tear_down_stream()

if __name__ == "__main__":
    main()
