import sys
import json
import grpc
import bfrt_grpc.client as gc

#===============================================================================================================================
"""
This module provides functions to interact with the BF Runtime server using gRPC.
It includes functions to connect to the server, retrieve table details, and manage indirect counters.
It also provides functionality to clear all tables and retrieve all tables and indirect counters.
"""
#===============================================================================================================================

#==========================================================
#============= G R P C  F U N C T I O N S =================
#==========================================================
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


def get_table_details(actual_tables, bfrt_info, tables,json_file):
    for table_name in actual_tables:
        table = bfrt_info.table_get(table_name)
        tables[table_name] = {
            "keys": [],
            "actions": []
        }
        # 🔑 Match (Key) Fields
        try:
            for key in table.info.key_field_name_list_get():
                match_type = table.info.key_field_match_type_get(key)
                tables[table_name]["keys"].append({
                    "name": key,
                    "match": match_type
                })
        except Exception as e:
            print(f"  Could not retrieve key fields: {e}")

        # 🎯 Actions and Parameters
        for action_name in table.info.action_name_list_get():
            if action_name == "NoAction":
                continue
            action_entry = {
                "name": action_name,
                "parameters": []
            }
            try:
                param_names = table.info.data_field_name_list_get(action_name)
                for param in param_names:
                    if "$COUNTER" in param:
                        continue
                    action_entry["parameters"].append(param)
            except Exception as e:
                print(f"  Failed to retrieve parameters for action '{action_name}': {e}")
            tables[table_name]["actions"].append(action_entry)
    # with open("table_info.json", "w") as f:
    with open(f"{json_file}.json", "w") as f:
        json.dump(tables, f, indent=2)
    return tables

def get_indirect_counter_details(indirect_counter_tables, bfrt_info, indirect_counters_info,json_file):
    for table_name in indirect_counter_tables:
        table = bfrt_info.table_get(table_name)
        indirect_counters_info[table_name] = {
            "keys": [],
        }
        try:
            for key in table.info.key_field_name_list_get():
                match_type = table.info.key_field_match_type_get(key)
                indirect_counters_info[table_name]["keys"].append({
                    "name": key,
                    "match": match_type
                })
        except Exception as e:
            print(f"  Could not retrieve key fields: {e}")
        data_fields_list =table.info.data_dict_allname
        indirect_counters_info[table_name]["data_fields"] = data_fields_list
    with open(f"{json_file}.json", "w") as f:
        json.dump(indirect_counters_info, f, indent=2)

    return indirect_counters_info    

def get_all_tbls():
    tables = {}
    indirect_counters_info = {}
    interface, dev_tgt, bfrt_info = gc_connect()
    temp = bfrt_info.table_name_list_get()
    actual_tables = [
        t for t in temp
        if ("pipe.Ingress." in t or "pipe.Egress." in t)
        and not any(skip in t for skip in ["miss", "counter", "routeId", "hash"])
    ]
    tables = get_table_details(actual_tables, bfrt_info, tables, "table_info")
    indirect_counter_tables = [
        t for t in temp
        if ("pipe.Ingress." in t or "pipe.Egress." in t)
        and "counter" in t
    ]
    indirect_counters_info = get_indirect_counter_details(indirect_counter_tables, bfrt_info, indirect_counters_info, "indirect_counter_info")
    return tables, indirect_counters_info, interface, dev_tgt, bfrt_info


def clear_all_tables(tables, dev_tgt, bfrt_info):
    for table_name in tables:
        if "eg_int_table" in table_name:
            continue
        table = bfrt_info.table_get(table_name)
        table.entry_del(dev_tgt, [])
