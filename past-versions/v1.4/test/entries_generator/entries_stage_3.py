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
    key = table.make_key([gc.KeyTuple('hdr.ethernet.src_addr', p4f.mac_to_int(f'00:00:00:00:00:01'))])
    data = table.make_data([gc.DataTuple('stats_idx', 1)], action_name="Ingress.ig_stg_3.send_to_cpu")
    table.entry_add(dev_tgt, [key], [data])

def main():
    interface, dev_tgt, bfrt_info = p4f.gc_connect()
    table_name = 'pipe.Ingress.ig_stg_3.is_sdn_tbl'
    table = p4f.get_table_info(table_name, bfrt_info)
    p4f.clear_table(table, dev_tgt)

    add_entries(table,dev_tgt)
    interface.tear_down_stream()

if __name__ == "__main__":
    main()

