import os
import ipaddress
import random
import csv
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


def create_entry_send_back(table,dev_tgt):
    key = table.make_key([gc.KeyTuple('ig_intr_md.ingress_port', 4)])
    data = table.make_data([gc.DataTuple('$COUNTER_SPEC_PKTS', 0), gc.DataTuple('$COUNTER_SPEC_BYTES', 0)], action_name="Ingress.ig_stg_5.send_back")
    table.entry_add(dev_tgt, [key], [data])

def create_entry_send_back_vlan(table,dev_tgt):
    # Get the current script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Directory where this script is located
    # Ensure the CSV is saved inside ../csv_files relative to this script's directory
    path = os.path.abspath(os.path.join(script_dir, "../csv_files"))
    print(f"Looking for CSV in: {path}")
    # Construct the full path to the CSV file
    file_path = os.path.join(path, 'flow_entries_stage_4.csv')
    # Read the CSV file
    with open(file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)  # Initialize inside the `with` block
        for row in csv_reader:
            if row["port"] == "5":
                key = table.make_key([gc.KeyTuple('ig_intr_md.ingress_port', 5), gc.KeyTuple('hdr.outer_vlan.vid', int(row["vlan"]))])
                data = table.make_data([gc.DataTuple('$COUNTER_SPEC_PKTS', 0), gc.DataTuple('$COUNTER_SPEC_BYTES', 0),gc.DataTuple('stats_idx', 2)], action_name="Ingress.ig_stg_5.send_back_vlan")
                table.entry_add(dev_tgt, [key], [data])
                
def main():
    interface, dev_tgt, bfrt_info = p4f.gc_connect()
    #First table 
    table_name_1= 'pipe.Ingress.ig_stg_5.ig_port_loop_tbl'
    table_1 = p4f.get_table_info(table_name_1, bfrt_info)
    p4f.clear_table(table_1, dev_tgt)

    #Second table
    table_name_2 = 'pipe.Ingress.ig_stg_5.ig_loop_counter'
    table_2 = p4f.get_table_info(table_name_2, bfrt_info)
    p4f.clear_table(table_2, dev_tgt)

    #Third table
    table_name_3 = 'pipe.Ingress.ig_stg_5.ig_vlan_loop_tbl'
    table_3 = p4f.get_table_info(table_name_3, bfrt_info)
    p4f.clear_table(table_3, dev_tgt)


    create_entry_send_back(table_1,dev_tgt)
    create_entry_send_back_vlan(table_3,dev_tgt)
    print("All entries have been added to the table.")
    # Cleanup
    interface.tear_down_stream()  
    
if __name__ == "__main__":
    main()
