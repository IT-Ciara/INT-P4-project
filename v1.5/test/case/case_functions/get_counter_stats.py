import sys
import os
import sys
import time
import bfrt_grpc.client as gc
import bfrt_grpc.bfruntime_pb2 as bfruntime_pb2
import struct
import socket
from case_functions import p4_functions as p4f

def print_data(data):
    # p4f.print_title("Data")
    print("-"*50)
    for key, value in data.items():
        key = key.replace("$", "")
        if "action_name" in key or "is_default" in key:
            continue
        else:
            print(f"{key:<25}: {value:<25}")
    print("-"*50)
    print("\n")

def print_stats(data):    
    print("-"*50)
    for key, value in data.items():
        key = key.replace("$", "")
        if "COUNTER_" in key:
            print(f"{key:<25}: {value:<25}")
    print("-"*50)
    print("\n")

def print_key(key):
    # p4f.print_title("Key")
    print("-"*50)
    for key, value in key.items():
        key = key.replace("$", "")
        if "ethernet" in key and "addr" in key:
            print(f"{key:<25}: {p4f.int_to_mac(value.get('value')):<25}")
        elif "ethernet" in key and "ether_type" in key:
            print(f"{key:<25}: {hex(value.get('value')):<25}")
        elif "ipv4" in key and "addr" in key:
            print(f"{key:<25}: {p4f.int_to_ip(value.get('value')):<25}")
        else:
            print(f"{key:<25}: {value.get('value'):<25}")

GREY = "\033[90m"
RESET = "\033[0m"  # Reset color after printing

def get_direct_counter_stats(dev_tgt, bfrt_info, table_name, print_all_data=False):
    print(GREY)
    entries = p4f.get_all_entries(table_name, dev_tgt, bfrt_info)
    if not entries:
        print("No entries in table" + RESET)
    else:
        for key, data in entries:
            print_key(key)
            if print_all_data:
                print_data(data)
            else:
                print_stats(data)

    print(RESET)  # Reset color to default
