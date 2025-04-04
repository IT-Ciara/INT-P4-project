#!/usr/bin/python3

import os
import sys
import time
import bfrt_grpc.client as gc  # Test import
width = 100

def get_all_entries(table_name, dev_tgt, bfrt_info):
    """Fetch all entries from a given table."""
    table = bfrt_info.table_get(table_name)
    entries = []
    for data, key in table.entry_get(dev_tgt, [], {"from_hw": True}):
        entries.append((key.to_dict(), data.to_dict()))
    return entries

def print_entries(entries):
    print("="*width)
    print(f"Table Entries Stats".center(width))
    print("="*width)
    stats = []
    if not entries:
        print("No entries found.")
    else:
        for key, data in entries:
            ingress_port = key.get('ig_intr_md.ingress_port', {}).get('value', 'N/A')
            user_flag = data.get('user_flag', 'N/A')
            packets = data.get('$COUNTER_SPEC_PKTS', 'N/A')
            bytes_count = data.get('$COUNTER_SPEC_BYTES', 'N/A')
            print(f"  Ingress Port: {ingress_port:<10} | User Flag: {user_flag:<10} | Packets: {packets:<10} | Bytes: {bytes_count:<15}")
            stats.append((ingress_port, user_flag, packets, bytes_count))
    print("-"*width)
    return stats


def main():
    # Attempt to connect to the BF Runtime server
    for bfrt_client_id in range(10):
        try:
            interface = gc.ClientInterface(
                grpc_addr="localhost:50052",
                client_id=bfrt_client_id,
                device_id=0,
                num_tries=1,
            )
            break
        except Exception:
            sys.exit(1)

    dev_tgt = gc.Target(device_id=0, pipe_id=0xffff)
    bfrt_info = interface.bfrt_info_get()

    if bfrt_client_id == 0:
        interface.bind_pipeline_config(bfrt_info.p4_name_get())

    table = 'pipe.Ingress.ig_ingress_port.ingress_port_tbl'
    # print(f"Table: {table}")
    entries = get_all_entries(table, dev_tgt, bfrt_info)
    stats = print_entries(entries)

    interface.tear_down_stream()

    return stats

    