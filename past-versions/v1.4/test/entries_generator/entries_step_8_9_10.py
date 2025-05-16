import os
import ipaddress
import random
import csv

drop_port_ranges = [(0, 3)]
drop_ether_dst_addr_ranges = [("00:00:00:00:00:05", "00:00:00:00:00:20")]
drop_vlan_vid_ranges = [(0x100, 0x200)]
drop_ipv4_range = ipaddress.ip_network("192.168.235.1/24", strict=False)

update_flows_port_ranges = [(4, 7)]
update_flows_ether_dst_addr_ranges = [("00:00:00:00:00:25", "00:00:00:00:00:40")]
update_flows_vlan_vid_ranges = [(0x300, 0x400)]
update_flows_ipv4_range = ipaddress.ip_network("192.168.240.1/24", strict=False)

def mac_to_int(mac):
    return int(mac.replace(":", ""), 16)

def int_to_mac(mac_int):
    return ":".join(f"{mac_int:012x}"[i:i+2] for i in range(0, 12, 2))

def clear_table(table):
    print(f"Clearing table: {table}")
    table.clear()

def generate_random_values(port_range, mac_range, vlan_range, ip_range, num_entries=4):
    try:
        ports = random.sample(range(port_range[0], port_range[1] + 1), num_entries)
        mac_addresses = random.sample(range(mac_to_int(mac_range[0]), mac_to_int(mac_range[1])), num_entries)
        mac_addresses = [int_to_mac(mac) for mac in mac_addresses]
        vlan_vids = random.sample(range(vlan_range[0], vlan_range[1] + 1), num_entries)
        ip_list = [str(ip) for ip in ip_range]
        ip_addresses = random.sample(ip_list, num_entries * 2)
        return ports, mac_addresses, vlan_vids, ip_addresses[:num_entries], ip_addresses[num_entries:]
    except ValueError:
        return [], [], [], [], []

def create_entries(table, port_range, mac_range, vlan_range, ip_range, action):
    values = generate_random_values(port_range, mac_range, vlan_range, ip_range)
    entries = []
    if all(values):
        for entry in zip(*values):
            if action == "drop":
                table.add_with_drop(ig_intr_md_ingress_port=entry[0], ethernet_dst_addr=entry[1], 
                                    ethernet_ether_type="0x8100", outer_vlan_vid=entry[2], 
                                    ipv4_src_addr=entry[3], ipv4_dst_addr=entry[4], stats_idx=1)
            elif action == "update_flows_counter":
                table.add_with_update_flows_counter(ig_intr_md_ingress_port=entry[0], ethernet_dst_addr=entry[1], 
                                                    ethernet_ether_type="0x8100", outer_vlan_vid=entry[2], 
                                                    ipv4_src_addr=entry[3], ipv4_dst_addr=entry[4],stats_idx=2)
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


def main_function():
    table = bfrt.p4_main_v1_4.pipe.Ingress.ig_contention_flow.contention_flow_tbl
    clear_table(table)
    clear_table(bfrt.p4_main_v1_4.pipe.Ingress.ig_contention_flow.tbl_contention_flow_counter)
    drop_values = create_entries(table, drop_port_ranges[0], drop_ether_dst_addr_ranges[0], drop_vlan_vid_ranges[0], drop_ipv4_range, "drop")    
    update_flows_values = create_entries(table, update_flows_port_ranges[0], update_flows_ether_dst_addr_ranges[0], update_flows_vlan_vid_ranges[0], update_flows_ipv4_range, "update_flows_counter")
    # table.dump()

    save_to_csv("flow_entries_8_9_10.csv", drop_values, update_flows_values)

    
    # Save to CSV
    save_to_csv("flow_entries_8_9_10.csv", drop_values, update_flows_values)

if __name__ == "__main__":
    main_function()
