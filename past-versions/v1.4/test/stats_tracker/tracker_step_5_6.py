#!/usr/bin/python3

import os
import sys
import time
import bfrt_grpc.client as gc  # Test import
width = 100

def get_all_tables(bfrt_info, dev_tgt):
    """Retrieve all table names that belong to Ingress or Egress."""
    temp = bfrt_info.table_name_list_get()
    return [t for t in temp if ".Ingress." in t or ".Egress." in t]

def get_all_entries(table_name, dev_tgt, bfrt_info):
    """Fetch all entries from a given table."""
    table = bfrt_info.table_get(table_name)
    entries = []
    for data, key in table.entry_get(dev_tgt, [], {"from_hw": True}):
        entries.append((key.to_dict(), data.to_dict()))
    return entries

def format_mac_address(mac):
    """Formats MAC address into standard notation XX:XX:XX:XX:XX:XX"""
    if isinstance(mac, int):  
        # Ensure it fits into a 6-byte MAC address
        return ":".join(f"{(mac >> (8 * i)) & 0xFF:02X}" for i in reversed(range(6)))
    elif isinstance(mac, str) and len(mac) == 12:  # If it's a full 12-character hex string
        return ":".join(mac[i:i+2].upper() for i in range(0, 12, 2))
    return mac  # Return as is if it's already formatted correctly

def print_direct_counter_entries(entries):
    if not entries:
        print("No entries found.")
    else:
        for key, data in entries:
            eth_src_address = format_mac_address(key.get('hdr.ethernet.src_addr', {}).get('value', 'N/A'))
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

    table = 'pipe.Ingress.ig_is_sdn_trace.is_sdn_tbl'
    print(f"\nTable: {table}")
    entries = get_all_entries(table, dev_tgt, bfrt_info)
    print_entries(entries, table, True)

    table = 'pipe.Ingress.ig_is_sdn_trace.is_sdn_trace_counter'
    print(f"\nTable: {table}")
    entries = get_all_entries(table, dev_tgt, bfrt_info)
    print_entries(entries, table, False)


    interface.tear_down_stream()
    