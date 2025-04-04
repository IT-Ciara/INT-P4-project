#!/usr/bin/python3

import os
import sys
import time
import bfrt_grpc.client as gc  # Test import
import p4_functions as p4f
width = 100


def print_direct_counter_entries(entries):
    if not entries:
        print("No entries found.")
    else:
        for key, data in entries:
            eth_src_address = p4f.format_mac_address(key.get('hdr.ethernet.src_addr', {}).get('value', 'N/A'))
            packets = data.get('$COUNTER_SPEC_PKTS', 'N/A')
            bytes_count = data.get('$COUNTER_SPEC_BYTES', 'N/A')
            print(f"Ethernet Source Address: {eth_src_address} | Packets: {packets}, Bytes: {bytes_count}")

def print_indirect_counter_entries(entries):
    if not entries:
        print("No entries found.")
    else:
        for key, data in entries:
            index = key.get('$COUNTER_INDEX', {}).get('value', 'N/A')
            packets = data.get('$COUNTER_SPEC_PKTS', 'N/A')
            bytes_count = data.get('$COUNTER_SPEC_BYTES', 'N/A')
            print(f" Index: {index} | Packets: {packets:<8} | Bytes: {bytes_count:<8}")
    

def print_entries(entries, table_name,direct_counter):
    print("="*width)
    print(f"Table Entries Stats".center(width))
    print("="*width)
    if direct_counter:
        print_direct_counter_entries(entries)
    else:
        print_indirect_counter_entries(entries)
    print("-"*width)
    print("\n")


def main():
    interface, dev_tgt, bfrt_info = p4f.gc_connect()
    table = 'pipe.Ingress.ig_stg_3.is_sdn_tbl'
    print(f"\nTable: {table}")
    entries = p4f.get_all_entries(table, dev_tgt, bfrt_info)
    print_entries(entries, table, True)

    table = 'pipe.Ingress.ig_stg_3.is_sdn_trace_counter'
    print(f"\nTable: {table}")
    entries = p4f.get_all_entries(table, dev_tgt, bfrt_info)
    print_entries(entries, table, False)

    interface.tear_down_stream()
    