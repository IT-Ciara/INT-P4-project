import pandas as pd
import json
import difflib

#========================================================================================================================
"""
Utility functions for managing and loading indirect counters from an Excel file.
This module provides functions to load indirect counter data, clear indirect counters, and retrieve counter values.
"""
#========================================================================================================================


def load_indirect_counter_data(file_path):
    """
    Load indirect counter data from an Excel file.
    :param file_path: Path to the Excel file containing indirect counter mappings.
    :return: List of dictionaries representing indirect counter mappings.
    """

    df = pd.read_excel(file_path, sheet_name='indirect_counter').fillna('')
    df.columns = df.columns.str.replace('\n', ' | ', regex=False)
    #Convert the df to a dictionary
    df_dict = df.to_dict(orient='records')
    return df_dict

def clear_all_indirect_counters(indirect_counter_tbls, dev_tgt, bfrt_info):
    """
    Clear all indirect counters in the provided list of tables.
    :param indirect_counter_tbls: List of indirect counter table names to clear.
    :param dev_tgt: Device target for the BFRT operations.
    :param bfrt_info: BFRT information object.
    """

    for table_name in indirect_counter_tbls:
        try:
            table = bfrt_info.table_get(table_name)
            table.entry_del(dev_tgt, [])
            print(f"  Cleared indirect counter: {table_name}")
        except Exception as e:
            print(f"  ⚠️ Failed to clear indirect counter '{table_name}': {e}")


def get_most_similar_counter(grpc_name, counter_dict):
    """
    Find the most similar counter name from a dictionary of counters based on a given gRPC name.
    :param grpc_name: The gRPC name to match against counter names.
    :param counter_dict: Dictionary containing counter names as keys.
    :return: The most similar counter name if found, otherwise None.
    """

    counter_names = list(counter_dict.keys())
    matches = difflib.get_close_matches(grpc_name, counter_names, n=1, cutoff=0.4)
    return matches[0] if matches else None

def print_counter_info(counter_name, details):
    """
    Print detailed information about a specific counter.
    :param counter_name: Name of the counter.
    :param details: Dictionary containing details of the counter.
    """

    print(f"  Counter Name: {counter_name}")
    for key, data_fields in details.items():
        if key == 'keys':
            print(f"    Keys: {data_fields}")
        elif key == 'data_fields':
            print(f"    Data Fields: {data_fields}")
        else:
            print(f"    {key}: {data_fields}")


def map_stages_to_indirect_counters(stage, indirect_counter_tbls, file_path):
    """
    Map stages to their corresponding indirect counters based on the provided stage and indirect counter tables.
    :param stage: Dictionary containing stage information.
    :param indirect_counter_tbls: Dictionary containing indirect counter table names and their details.
    :param file_path: Path to the Excel file containing indirect counter mappings.
    :return: Dictionary mapping stage names to their corresponding indirect counters.
    """

    indirect_counters_dict = load_indirect_counter_data(file_path)
    stage_map = {}

    # Iterate through each row of the loaded indirect counter mappings
    for row in indirect_counters_dict:
        for stage_name, indirect_counter in row.items():
            # Initialize empty counters for each stage
            if stage_name not in stage_map:
                stage_map[stage_name] = {"counters": []}
            if stage.get(stage_name, {}).get("value") == "NO" or "Stg2" in stage_name:
                for counter_name, counter_data in indirect_counter_tbls.items():
                    if indirect_counter in counter_name:
                        # Add to counters list
                        stage_map[stage_name]["counters"].append({
                            "name": counter_name,
                            "keys": [k["name"] for k in counter_data.get("keys", [])],
                            "data_fields": counter_data.get("data_fields", {})
                        })

    return stage_map
def get_counter_values_by_stage(stage_name, stage_map, bfrt_info, dev_tgt):
    """
    Retrieve counter values for a specific stage from the stage map.
    :param stage_name: Name of the stage for which to retrieve counter values.
    :param stage_map: Dictionary mapping stage names to their corresponding counters.
    :param bfrt_info: BFRT information object.
    :param dev_tgt: Device target for the BFRT operations.
    :return: List of dictionaries containing counter values for the specified stage.
    """

    if stage_name not in stage_map:
        print(f"Stage '{stage_name}' not found in stage_map.")
        return []

    if "counters" not in stage_map[stage_name]:
        print(f"No 'counters' defined for stage '{stage_name}'.")
        return []

    results = []
    for counter in stage_map[stage_name]["counters"]:
        table_name = counter["name"]
        if not table_name:
            continue

        try:
            table = bfrt_info.table_get(table_name)
            entries = table.entry_get(dev_tgt, [], {"from_hw": True})
            print(f"▶ Counter: {table_name}")
            for idx, (data, key) in enumerate(entries):
                if idx > 1:
                    break
                key_dict = key.to_dict()
                data_dict = data.to_dict()
                results.append({
                    "table": table_name,
                    "key": key_dict,
                    "packets": data_dict.get("$COUNTER_SPEC_PKTS", 0),
                    "bytes": data_dict.get("$COUNTER_SPEC_BYTES", 0)
                })
                print(f" Entry {idx:<2}: |  Packets: {data_dict.get('$COUNTER_SPEC_PKTS', 0):<5} | Bytes: {data_dict.get('$COUNTER_SPEC_BYTES', 0):<5}")
        except Exception as e:
            print(f"  ⚠️ Failed to read from {table_name}: {e}")
            continue

    return results

def get_indirect_counter_values(indirect_counters, dev_tgt, bfrt_info, target_index=0):
    """
    Retrieve values from indirect counters based on the provided indirect counters mapping.
    :param indirect_counters: Dictionary containing indirect counter names and their details.
    :param dev_tgt: Device target for the BFRT operations.
    :param bfrt_info: BFRT information object.
    :param target_index: Specific index to filter the counters (default is 0).
    :return: Integer value of the counter for the specified index.
    """

    counter_value = 0
    for counter_name, _ in indirect_counters.items():
        table = bfrt_info.table_get(counter_name)
        entries = table.entry_get(dev_tgt, [], {"from_hw": True})
        # print(f"\nCounter: {counter_name}")
        # print("-" * 60)
        for data, key in entries:
            key_dict = key.to_dict()
            data_dict = data.to_dict()

            # Extract index value (usually under $COUNTER_INDEX or similar)
            index = None
            for k, v in key_dict.items():
                if "$COUNTER_INDEX" in k or "INDEX" in k.upper():
                    index = v['value'] if isinstance(v, dict) and 'value' in v else v
                    break

            # Skip if a specific index is provided and this isn't it
            if target_index is not None and index != target_index:
                continue

            keys_str = ", ".join(
                f"{k}: {v['value'] if isinstance(v, dict) and 'value' in v else v}"
                for k, v in key_dict.items()
            )
            # Extract counter value
            counter_value = data_dict.get("$COUNTER_SPEC_PKTS", 0)
            counters_str = ", ".join(
                f"{k}: {v}" for k, v in data_dict.items() if k.startswith("$COUNTER_SPEC_")
            )
            # print(f"Keys     : {keys_str}")
            # print(f"Counters : {counters_str}")
            # print("-" * 60)
    return int(counter_value)


def get_direct_counters(tables, dev_tgt, bfrt_info):
    """
    Retrieve direct counter values from specified tables.
    :param tables: List of table names to retrieve direct counters from.
    :param dev_tgt: Device target for the BFRT operations.
    :param bfrt_info: BFRT information object.
    :return: Integer value of the counter from the first table.
    """
    
    counter_value = 0
    for table_name in tables:
        table = bfrt_info.table_get(table_name)
        entries = table.entry_get(dev_tgt, [], {"from_hw": True})
        # print(f"\nTable: {table_name}")
        # print("-" * 60)
        for data, key in entries:
            key_dict = key.to_dict()
            data_dict = data.to_dict()
            keys_str = ", ".join(
                f"{k}: {v['value'] if isinstance(v, dict) and 'value' in v else v}"
                for k, v in key_dict.items()
            )
            counter_value = data_dict.get("$COUNTER_SPEC_PKTS", 0)
            counters_str = ", ".join(
                f"{k}: {v}" for k, v in data_dict.items() if k.startswith("$COUNTER_SPEC_")
            )
            action = data_dict.get("action_name", "N/A")
            # print(f"Keys     : {keys_str}")
            # print(f"Action   : {action}")
            # print(f"Counters : {counters_str}")
            # print("-" * 60)

    #RETURN THE COUNTER VALUE 
    return int(counter_value)
