import pandas as pd
import json

#==================================================================================================================================
"""
This module provides functions to read data from an Excel file containing pipeline stages and their associated tables and counters.
It includes functions to retrieve all DataFrames from the file, extract indirect counters and tables, and enrich stage information with metadata from BFRT.
"""
#==================================================================================================================================


def get_all_dfs(file_path='./functions/cases.xlsx'):
    """
    Read all sheets from an Excel file and return a dictionary of DataFrames.
    :param file_path: Path to the Excel file.
    :return: Dictionary where keys are sheet names and values are DataFrames.
    """
    cases_df = pd.read_excel(file_path, sheet_name='Cases').fillna('')
    cases_df.columns = cases_df.columns.str.replace('\n', ' | ', regex=False)
    Stg_tbls_df = pd.read_excel(file_path, sheet_name='Stg-tbls').fillna('')
    indirect_counter_df = pd.read_excel(file_path, sheet_name='indirect_counter').fillna('')
    counters_df = pd.read_excel(file_path, sheet_name='counters').fillna('')
    counters_df.columns = counters_df.columns.str.replace('\n', ' | ', regex=False)
    return cases_df, Stg_tbls_df, indirect_counter_df, counters_df


#================================== G E T  S T A G E S  F U N C T I O N S ================================
#=========================================================================================================

def get_indirect_counters_details(counters, bfrt_info):
    """
    Retrieve details of indirect counters from the bfrt_info object.
    :param counters: List of counter names to retrieve details for.
    :param bfrt_info: BFRT information object.
    :return: Dictionary containing details of the indirect counters.
    """
    indirect_counters_info = {}
    for counter_name in counters:
        table = bfrt_info.table_get(counter_name)
        indirect_counters_info[counter_name] = {
            "keys": [],
        }
        try:
            for key in table.info.key_field_name_list_get():
                match_type = table.info.key_field_match_type_get(key)
                indirect_counters_info[counter_name]["keys"].append({
                    "name": key,
                    "match": match_type
                })
        except Exception as e:
            print(f"  Could not retrieve key fields: {e}")
        data_fields_list = table.info.data_dict_allname
        indirect_counters_info[counter_name]["data_fields"] = data_fields_list
    return indirect_counters_info

def get_all_counters(bfrt_info):
    """
    Retrieve all indirect counters from the BFRT information object.
    :param bfrt_info: BFRT information object.
    :return: Dictionary containing details of all indirect counters.
    """
    indirect_counter = []
    all_tables = bfrt_info.table_name_list_get()
    for table_name in all_tables:
        if "pipe.Ingress." in table_name or "pipe.Egress." in table_name:
            if 'counter' in table_name:
                indirect_counter.append(table_name)
    return get_indirect_counters_details(indirect_counter, bfrt_info)


def get_table_details(tables, bfrt_info):
    """
    Retrieve details of specified tables from the BFRT information object.
    :param tables: List of table names to retrieve details for.
    :param bfrt_info: BFRT information object.
    :return: Dictionary containing details of the specified tables.
    """

    tables_dict = {}
    for table_name in tables:
        table = bfrt_info.table_get(table_name)
        keys = table.info.key_field_name_list_get()
        actions = table.info.action_name_list_get()
        tables_dict[table_name] = {
            "grpc_name": table_name,
            "keys": [],
            "actions": []
        }
        for key in keys:
            match_type = table.info.key_field_match_type_get(key)
            tables_dict[table_name]["keys"].append({
                "name": key,
                "match": match_type
            })
        for action_name in actions:
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
                tables_dict[table_name]["actions"].append(action_entry)
            except Exception as e:
                print(f"  Could not retrieve action parameters: {e}")
    return tables_dict



def get_all_tables(bfrt_info):
    """
    Retrieve all tables from the BFRT information object.
    :param bfrt_info: BFRT information object.
    :return: Dictionary containing details of all tables.
    """

    tables = []
    all_tables = bfrt_info.table_name_list_get()
    for table_name in all_tables:
        if "pipe.Ingress." in table_name or "pipe.Egress." in table_name:
            if any(x in table_name for x in ['miss', 'counter', 'routeId', 'hash']):
                continue
            tables.append(table_name)
    return get_table_details(tables, bfrt_info)



def get_main_stages(bfrt_info, tables_df,counters_df):
    """
    Extract main stages from the provided DataFrame and enrich them with metadata from BFRT.
    :param bfrt_info: BFRT information object.
    :param tables_df: DataFrame containing table names.
    :param counters_df: DataFrame containing counter names.
    :return: Dictionary containing enriched stage information.
    """
    stages = {}
    tables_df.columns = tables_df.columns.str.replace('\n', ' | ', regex=False)
    counters_df.columns = counters_df.columns.str.replace('\n', ' | ', regex=False)
    for col in tables_df.columns:
        stage_name = col.strip()
        table_values = tables_df[col].dropna().astype(str).str.strip().tolist()
        counter_values = counters_df[col].dropna().astype(str).str.strip().tolist() if col in counters_df.columns else []
        table_values = [val for val in table_values if val]
        counter_values = [val for val in counter_values if val]
        stages[stage_name] = {
            'value': "",
            'Tables': table_values,
            'Indirect Counters': counter_values
        }
    # Fetch metadata from BFRT
    tables = get_all_tables(bfrt_info)
    indirect_counters = get_all_counters(bfrt_info)
    # Combine everything
    enriched_stages = {}
    for stage, data in stages.items():
        stage_info = {
            'value' : "",
            'Tables': {},
            'Indirect Counters': {}
        }
        # Match and enrich table info
        for tbl_name in data['Tables']:
            fq_table = next((t for t in tables if t.endswith(tbl_name)), None)
            if fq_table and fq_table in tables:
                stage_info['Tables'][fq_table] = tables[fq_table]
            else:
                stage_info['Tables'][tbl_name] = {"error": "Table metadata not found"}
        # Match and enrich counter info
        for ctr_name in data['Indirect Counters']:
            fq_counter = next((c for c in indirect_counters if c.endswith(ctr_name)), None)
            if fq_counter and fq_counter in indirect_counters:
                stage_info['Indirect Counters'][fq_counter] = indirect_counters[fq_counter]
            else:
                stage_info['Indirect Counters'][ctr_name] = {"error": "Counter metadata not found"}
        enriched_stages[stage] = stage_info
    # Save to JSON
    with open("stage_mapping.json", "w") as f:
        json.dump(enriched_stages, f, indent=4)
    return enriched_stages