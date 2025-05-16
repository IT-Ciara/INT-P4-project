#!/usr/bin/python3

import os
import sys
import time
import bfrt_grpc.client as gc  # Test import
import p4_functions as p4f
width = 100 

def print_entries(entries):
    p4f.print_entry_stats()
    stats = []
    if not entries:
        print("No entries found.")
    else:
        for key, data in entries:
            ingress_port = key.get('ig_intr_md.ingress_port', {}).get('value', 'N/A')
            user_port = data.get('user_port', 'N/A')
            packets = data.get('$COUNTER_SPEC_PKTS', 'N/A')
            bytes_count = data.get('$COUNTER_SPEC_BYTES', 'N/A')
            print(f"  Ingress Port: {ingress_port:<10} | User Flag: {user_port:<10} | Packets: {packets:<10} | Bytes: {bytes_count:<15}")
            stats.append((ingress_port, user_port, packets, bytes_count))
    print("-"*width)
    return stats

def main():
    interface, dev_tgt, bfrt_info = p4f.gc_connect()
    table = 'pipe.Ingress.ig_stg_2.ingress_port_tbl'
    entries = p4f.get_all_entries(table, dev_tgt, bfrt_info)
    stats = print_entries(entries)

    interface.tear_down_stream()

    return stats

    