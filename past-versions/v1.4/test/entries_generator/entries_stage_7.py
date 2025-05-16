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
    key = table.make_key([gc.KeyTuple('hdr.ethernet.ether_type', 0x8842)])
    data = table.make_data([], action_name="Ingress.ig_stg_7.set_polka_md")
    table.entry_add(dev_tgt, [key], [data])

def main():
    interface, dev_tgt, bfrt_info = p4f.gc_connect()
    table_name = 'pipe.Ingress.ig_stg_7.ig_polka_type_tbl'
    table = p4f.get_table_info(table_name, bfrt_info)
    p4f.clear_table(table, dev_tgt)

    add_entries(table,dev_tgt)
    interface.tear_down_stream()

if __name__ == "__main__":
    main()

