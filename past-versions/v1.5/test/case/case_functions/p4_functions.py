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
width = 120



#===============================================================================
# Helper functions M A I N   S C R I P T
#===============================================================================


def get_color(name):
    name = name.upper()
    RED = "\033[91m"
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"  
    GREY = "\033[90m"
    if name == 'RED':
        return RED
    elif name == 'GREEN':
        return GREEN
    elif name == 'BLUE':
        return BLUE
    elif name == 'YELLOW':
        return YELLOW
    elif name == 'RESET':
        return RESET
    elif name == 'GREY':
        return GREY
    else:
        return RESET
    

def add_entries(function):
    width = 100
    print("\n\n")
    print(f"{get_color('GREY')}{'='*width}{get_color('RESET')}")
    print(f"{get_color('GREY')}{'A D D I N G   E N T R I E S'.center(width)}{get_color('RESET')}")
    print(f"{get_color('GREY')}{'='*width}{get_color('RESET')}")
    function.main()


def print_main(stage_name):
    print(get_color('BLUE'))
    stage_name = stage_name.upper()
    # Put a space between each character in the stage name
    stage_name = "  ".join(stage_name)
    print("\n")
    print(f"{get_color('BLUE')}{'='*width}{get_color('RESET')}")
    print(f"{get_color('BLUE')}{'='*width}{get_color('RESET')}")
    print(f"{get_color('BLUE')}{stage_name.center(width)}{get_color('RESET')}")
    print(f"{get_color('BLUE')}{'='*width}{get_color('RESET')}")
    print(f"{get_color('BLUE')}{'='*width}{get_color('RESET')}")

def clear_all_tables(bfrt_info, dev_tgt):
    """Clear all tables in the pipeline, excluding those with constant entries or explicitly skipped ones."""
    skip_tables = {
        "pipe.Egress.routeId_high_lower",
        "pipe.Egress.routeId_high_upper",
        "pipe.Egress.routeId_low_lower",
        "pipe.Egress.routeId_low_upper",
        "pipe.Ingress.hash.compute",
    }
    tables = get_all_tables(bfrt_info, dev_tgt)
    for table_name in tables:
        if table_name in skip_tables:
            # print(f"[SKIP] Skipping table: {table_name}")
            continue
        # print(f"Clearing table: {table_name}")
        # Optional filtering logic remains (if needed):
        if "routeId" not in table_name or "hash" not in table_name:
            if "ig_input_port" not in table_name and "eg_int_table" not in table_name:
                try:
                    table = bfrt_info.table_get(table_name)
                    clear_table(table, dev_tgt)
                except KeyError:
                    print(f"[WARNING] Table '{table_name}' not found in bfrt_info.")

#===============================================================================
# Helper functions E N T R I E S   G E N E R A T O R
#===============================================================================

def gc_connect():
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
    return interface, dev_tgt, bfrt_info


def get_table_info(table_name, bfrt_info):
    table = bfrt_info.table_get(table_name)
    print("Table Information:\n", table.info)
    return table

def clear_table(table, dev_tgt):
    table.entry_del(dev_tgt, [])
    # print("All entries have been deleted from the table.")


def get_all_entries(table_name, dev_tgt, bfrt_info):
    """Fetch all entries from a given table."""
    table = bfrt_info.table_get(table_name)
    entries = []
    for data, key in table.entry_get(dev_tgt, [], {"from_hw": True}):
        entries.append((key.to_dict(), data.to_dict()))
    return entries

def mac_to_int(mac):
    """Convert MAC address string to an integer."""
    return int(mac.replace(":", ""), 16)

def ip_to_int(ip_str):
    """Convert IPv4 address string to an integer."""
    return struct.unpack("!I", socket.inet_aton(ip_str))[0]

def eth_type_to_int(eth_type):
    """Convert Ethernet type string to an integer."""
    return int(eth_type, 16)




def int_to_ip(ip_int):
    """Convert an integer to an IPv4 address string."""
    return str(ipaddress.IPv4Address(ip_int))


def int_to_mac(mac_int):
    return ":".join(f"{mac_int:012x}"[i:i+2] for i in range(0, 12, 2))

def print_entry_stats():
    width = 100
    print("="*width)
    print(f"Table Entries Stats".center(width))
    print("="*width)

def print_title(title):
    title = title.upper()
    # Put a space between each character in the stage name
    # title = "  ".join(title)
    width = 50
    print("-"*width)
    print(f"{title}".center(width))
    print("-"*width)


def get_interfaces():
    interfaces = []
    #even numbers from 0 to 30 
    for i in range(0, 32, 2):
        interfaces.append(f"veth{str(i)}")
    return interfaces


#===============================================================================
# Helper functions S T A T S   T R A C K E R
#===============================================================================

def format_mac_address(mac):
    """Formats MAC address into standard notation XX:XX:XX:XX:XX:XX"""
    if isinstance(mac, int):  
        # Ensure it fits into a 6-byte MAC address
        return ":".join(f"{(mac >> (8 * i)) & 0xFF:02X}" for i in reversed(range(6)))
    elif isinstance(mac, str) and len(mac) == 12:  # If it's a full 12-character hex string
        return ":".join(mac[i:i+2].upper() for i in range(0, 12, 2))
    return mac  # Return as is if it's already formatted correctly



#===============================================================================
# Helper functions P K T   G E N E R A T O R
#===============================================================================

def get_all_tables(bfrt_info, dev_tgt):
    """Retrieve all table names that belong to Ingress or Egress."""
    temp = bfrt_info.table_name_list_get()
    return [t for t in temp if ".Ingress." in t or ".Egress." in t]


def print_console(color,text,width=120,character="=",space=True,top=False,break_line=True):
    if break_line:
        print("\n")
    if space:
        text = " ".join(text)
    text = text.upper()

    if character == " " or character == "":
        print(f"{get_color(color)}{text.center(width)}{get_color('RESET')}")    

    else:
        if character == "=" or top:
            print(f"{get_color(color)}{character*width}{get_color('RESET')}")
        print(f"{get_color(color)}{text.center(width)}{get_color('RESET')}")
        print(f"{get_color(color)}{character*width}{get_color('RESET')}")
