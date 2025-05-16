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

drop_port_ranges = [(0, 3)]
drop_ether_dst_addr_ranges = [("00:00:00:00:00:05", "00:00:00:00:00:20")]
drop_vlan_vid_ranges = [(0x100, 0x200)]
drop_ipv4_range = ipaddress.ip_network("192.168.235.1/24", strict=False)

update_flows_port_ranges = [(4, 7)]
update_flows_ether_dst_addr_ranges = [("00:00:00:00:00:25", "00:00:00:00:00:40")]
update_flows_vlan_vid_ranges = [(0x300, 0x400)]
update_flows_ipv4_range = ipaddress.ip_network("192.168.240.1/24", strict=False)

def generate_random_values(port_range, mac_range, vlan_range, ip_range, num_entries=4):
    try:
        ports = random.sample(range(port_range[0], port_range[1] + 1), num_entries)
        mac_addresses = random.sample(range(p4f.mac_to_int(mac_range[0]), p4f.mac_to_int(mac_range[1])), num_entries)
        mac_addresses = [p4f.int_to_mac(mac) for mac in mac_addresses]
        vlan_vids = random.sample(range(vlan_range[0], vlan_range[1] + 1), num_entries)
        ip_list = [str(ip) for ip in ip_range]
        ip_addresses = random.sample(ip_list, num_entries * 2)
        return ports, mac_addresses, vlan_vids, ip_addresses[:num_entries], ip_addresses[num_entries:]
    except ValueError:
        return [], [], [], [], []
    
def add_entry(table, target, port, mac, vlan, src_ip, dst_ip, action):
    key = table.make_key([
        gc.KeyTuple('ig_intr_md.ingress_port', port),
        gc.KeyTuple('hdr.ethernet.dst_addr', p4f.mac_to_int(mac)),
        gc.KeyTuple('hdr.ethernet.ether_type', 0x8100),
        gc.KeyTuple('hdr.outer_vlan.vid', vlan),
        gc.KeyTuple('hdr.ipv4.src_addr', p4f.ip_to_int(src_ip)),
        gc.KeyTuple('hdr.ipv4.dst_addr', p4f.ip_to_int(dst_ip))
    ])
    
    data = table.make_data([
        gc.DataTuple('$COUNTER_SPEC_PKTS', 0),
        gc.DataTuple('$COUNTER_SPEC_BYTES', 0)
    ], action_name=action)
    
    table.entry_add(target, [key], [data])

def create_entries(table, port_range, mac_range, vlan_range, ip_range, action,target):
    values = generate_random_values(port_range, mac_range, vlan_range, ip_range)
    entries = []
    if all(values):
        for entry in zip(*values):
            if action == "drop":
                add_entry(table, target, entry[0], entry[1], entry[2], entry[3], entry[4], "Ingress.ig_stg_4.drop")
            entries.append({
                "port": entry[0],
                "mac": entry[1],
                "vlan": entry[2],
                "src_ip": entry[3],
                "dst_ip": entry[4],
                "action": action
            })
    return entries

def save_to_csv(filename, drop_values, update_flows_values):
    with open(filename, mode='w', newline='') as file:
        fieldnames = ["port", "mac", "vlan", "src_ip", "dst_ip", "action"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(drop_values + update_flows_values)

def save_to_csv(filename, drop_values, update_flows_values):
    try:
        # Get the current script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Directory where this script is located
        # Ensure the CSV is saved inside ../csv_files relative to this script's directory
        path = os.path.abspath(os.path.join(script_dir, "../csv_files"))
        os.makedirs(path, exist_ok=True)  # Ensure the directory exists
        # Construct the full path to the CSV file
        file_path = os.path.join(path, filename)
        with open(file_path, mode='w', newline='') as file:
            fieldnames = ["port", "mac", "vlan", "src_ip", "dst_ip", "action"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()  # Write CSV headers
            all_entries = drop_values + update_flows_values

            if all_entries:
                writer.writerows(all_entries)
            else:
                print("No entries to write.")

    except Exception as e:
        print(f"Error writing to CSV: {e}")


def main():
    interface, dev_tgt, bfrt_info = p4f.gc_connect()
    table_name = 'pipe.Ingress.ig_stg_4.contention_flow_tbl'
    table = p4f.get_table_info(table_name, bfrt_info)
    p4f.clear_table(table, dev_tgt)
    drop_values = create_entries(table, drop_port_ranges[0], drop_ether_dst_addr_ranges[0], drop_vlan_vid_ranges[0], drop_ipv4_range, "drop",dev_tgt)
    update_flows_values = create_entries(table, update_flows_port_ranges[0], update_flows_ether_dst_addr_ranges[0], update_flows_vlan_vid_ranges[0], update_flows_ipv4_range, "update_flows_counter",dev_tgt)
    save_to_csv("flow_entries_stage_4.csv", drop_values, update_flows_values)
    # Cleanup
    interface.tear_down_stream()    

if __name__ == "__main__":
    main()
